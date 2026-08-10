import logging
from datetime import datetime, timedelta, timezone
from sqlalchemy import select, and_, func
from app.tasks.celery_app import celery_app
from app.core.database import AsyncSessionLocal
from app.models.appointment import Appointment, AppointmentStatus
from app.models.customer import Customer
from app.models.business import Business
from app.models.saas import Plan
from app.models.subscription import Subscription

logger = logging.getLogger(__name__)

@celery_app.task(name="run_winback_campaigns")
def run_winback_campaigns():
    """Celery Beat daily campaign task to re-engage inactive customers."""
    import asyncio
    asyncio.run(_async_run_winback_campaigns())

async def _async_run_winback_campaigns():
    now = datetime.now(timezone.utc)
    cutoff_date = now - timedelta(days=30)
    
    async with AsyncSessionLocal() as session:
        # Find active subscriptions for plans that allow winback campaigns
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
        res = await session.execute(stmt)
        active_campaign_businesses = res.all()
        
        for sub, plan, business in active_campaign_businesses:
            # Query inactive customers for this business
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
                .having(func.max(Appointment.start_time) < cutoff_date)
            )
            cust_res = await session.execute(cust_stmt)
            inactive_customers = cust_res.all()
            
            for customer, last_visit in inactive_customers:
                logger.info(
                    f"[WIN-BACK CAMPAIGN] Dispatched WhatsApp win-back message to {customer.name or customer.phone_number} "
                    f"for Business '{business.name}' (Last visit: {last_visit.strftime('%Y-%m-%d')})"
                )
