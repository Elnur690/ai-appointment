import logging
from datetime import datetime, timedelta, timezone
from sqlalchemy import select, and_, func
from app.tasks.celery_app import celery_app
from app.core.database import AsyncSessionLocal, engine
from app.core.config import settings
from app.models.appointment import Appointment, AppointmentStatus
from app.models.customer import Customer
from app.models.business import Branch, Business
from app.models.saas import Plan
from app.models.subscription import Subscription
from app.integrations.whatsapp.client import EvolutionAPIClient
from app.integrations.whatsapp.message_sender import WhatsAppMessageSender

logger = logging.getLogger(__name__)


@celery_app.task(name="run_winback_campaigns")
def run_winback_campaigns():
    """Celery Beat daily campaign task to re-engage inactive customers via WhatsApp."""
    import asyncio
    asyncio.run(_async_run_winback_campaigns())


async def _async_run_winback_campaigns():
    now = datetime.now(timezone.utc)
    cutoff_date = now - timedelta(days=30)
    window_start = now - timedelta(days=31)

    evo_client = EvolutionAPIClient(base_url=settings.EVOLUTION_API_URL, api_key=settings.EVOLUTION_API_KEY)
    sender = WhatsAppMessageSender(evo_client)
    redis_client = None
    try:
        import redis.asyncio as aioredis
        redis_client = aioredis.from_url(settings.REDIS_URL, decode_responses=True)
    except Exception as exc:
        logger.warning(f"Win-back Redis dedupe unavailable, relying on 30-31d window: {exc}")

    try:
        async with AsyncSessionLocal() as session:
            stmt = (
                select(Subscription, Plan, Business)
                .join(Plan, Subscription.plan_id == Plan.id)
                .join(Business, Subscription.business_id == Business.id)
                .where(
                    and_(
                        Plan.allows_winback_campaigns.is_(True),
                        Subscription.status == "active",
                        Business.is_active.is_(True),
                    )
                )
            )
            active_campaign_businesses = (await session.execute(stmt)).all()

            for sub, plan, business in active_campaign_businesses:
                branch = (
                    await session.execute(
                        select(Branch).where(Branch.business_id == business.id, Branch.is_active.is_(True))
                    )
                ).scalars().first()
                instance_name = (
                    (branch.whatsapp_instance_id if branch else None)
                    or f"randevu_{str(business.id)[:8]}_main"
                )

                cust_stmt = (
                    select(Customer, func.max(Appointment.start_time).label("last_visit"))
                    .join(Appointment, Customer.id == Appointment.customer_id)
                    .where(
                        and_(
                            Customer.business_id == business.id,
                            Appointment.status == AppointmentStatus.completed,
                        )
                    )
                    .group_by(Customer.id)
                    .having(
                        and_(
                            func.max(Appointment.start_time) < cutoff_date,
                            func.max(Appointment.start_time) >= window_start,
                        )
                    )
                )
                inactive_customers = (await session.execute(cust_stmt)).all()

                for customer, last_visit in inactive_customers:
                    dedupe_key = f"winback_sent:{business.id}:{customer.id}"
                    if redis_client is not None:
                        try:
                            already_sent = await redis_client.get(dedupe_key)
                            if already_sent:
                                continue
                        except Exception:
                            pass

                    if customer.phone_number and not customer.phone_number.startswith("tg:"):
                        msg = (
                            f"Salam{(', ' + customer.name) if customer.name else ''}! "
                            f"{business.name} olaraq sizi yenidən görməyə şad olarıq. "
                            f"Yeni randevu üçün bu mesaja cavab yazmağınız kifayətdir."
                        )
                        await sender.send_response(
                            instance_name=instance_name,
                            to_phone=customer.phone_number,
                            text=msg,
                        )
                        if redis_client is not None:
                            try:
                                await redis_client.set(dedupe_key, "1", ex=30 * 24 * 3600)
                            except Exception:
                                pass
                    logger.info(
                        f"[WIN-BACK CAMPAIGN] Dispatched win-back message to {customer.name or customer.phone_number} "
                        f"for Business '{business.name}' (Last visit: {last_visit.strftime('%Y-%m-%d')})"
                    )
    finally:
        if redis_client is not None:
            try:
                await redis_client.aclose()
            except Exception:
                pass
        await evo_client.close()
        await engine.dispose()
