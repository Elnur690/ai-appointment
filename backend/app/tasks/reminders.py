import logging
from datetime import datetime, timedelta, timezone
from sqlalchemy import select, and_
from app.tasks.celery_app import celery_app
from app.core.database import AsyncSessionLocal, engine
from app.core.config import settings
from app.models.appointment import Appointment, AppointmentStatus
from app.models.business import Branch, Business
from app.models.customer import Customer
from app.models.service import Service
from app.integrations.whatsapp.client import EvolutionAPIClient
from app.integrations.whatsapp.message_sender import WhatsAppMessageSender

logger = logging.getLogger(__name__)


async def _dispatch_outbound_reminder(
    sender: WhatsAppMessageSender,
    business: Business | None,
    branch: Branch | None,
    customer: Customer | None,
    text: str,
) -> None:
    if not customer or not customer.phone_number:
        return
    phone = customer.phone_number.strip()
    if phone.startswith("tg:"):
        bot_token = ((business.default_ai_tone_config or {}).get("telegram_bot_token") or "").strip() if business else ""
        chat_id = phone[3:]
        if bot_token and chat_id:
            import httpx
            try:
                async with httpx.AsyncClient(timeout=10.0) as client:
                    await client.post(
                        f"https://api.telegram.org/bot{bot_token}/sendMessage",
                        json={"chat_id": chat_id, "text": text},
                    )
            except Exception as exc:
                logger.warning(f"Telegram reminder dispatch failed: {exc}")
        return

    instance_name = (
        (branch.whatsapp_instance_id if branch else None)
        or (f"randevu_{str(business.id)[:8]}_main" if business else None)
    )
    if instance_name:
        await sender.send_response(instance_name=instance_name, to_phone=phone, text=text)


@celery_app.task(name="send_appointment_reminders")
def send_appointment_reminders():
    """Celery Beat task running every 5 minutes to send 24h and 2h appointment reminders."""
    import asyncio
    asyncio.run(_async_send_reminders())


async def _async_send_reminders():
    now = datetime.now(timezone.utc)
    window_24h_start = now + timedelta(hours=23, minutes=55)
    window_24h_end = now + timedelta(hours=24, minutes=5)
    window_2h_start = now + timedelta(hours=1, minutes=55)
    window_2h_end = now + timedelta(hours=2, minutes=5)

    evo_client = EvolutionAPIClient(base_url=settings.EVOLUTION_API_URL, api_key=settings.EVOLUTION_API_KEY)
    sender = WhatsAppMessageSender(evo_client)

    try:
        async with AsyncSessionLocal() as session:
            for label, w_start, w_end, sent_col in [
                ("24h", window_24h_start, window_24h_end, Appointment.reminder_24h_sent_at),
                ("2h", window_2h_start, window_2h_end, Appointment.reminder_2h_sent_at),
            ]:
                stmt = (
                    select(Appointment, Customer, Service, Branch, Business)
                    .outerjoin(Customer, Appointment.customer_id == Customer.id)
                    .outerjoin(Service, Appointment.service_id == Service.id)
                    .outerjoin(Branch, Appointment.branch_id == Branch.id)
                    .outerjoin(Business, Appointment.business_id == Business.id)
                    .where(
                        and_(
                            Appointment.status == AppointmentStatus.confirmed,
                            Appointment.start_time >= w_start,
                            Appointment.start_time <= w_end,
                            sent_col.is_(None),
                        )
                    )
                )
                rows = (await session.execute(stmt)).all()
                for appt, cust, svc, br, biz in rows:
                    time_str = appt.start_time.strftime("%Y-%m-%d %H:%M")
                    svc_name = svc.name if svc else "Randevu"
                    biz_name = biz.name if biz else "Randevu.vip"
                    msg = (
                        f"Salam{(', ' + cust.name) if cust and cust.name else ''}! "
                        f"{biz_name} xatırladır: {time_str} tarixində '{svc_name}' randevunuz var."
                    )
                    await _dispatch_outbound_reminder(sender, biz, br, cust, msg)
                    if label == "24h":
                        appt.reminder_24h_sent_at = now
                    else:
                        appt.reminder_2h_sent_at = now
                    logger.info(f"Dispatched {label} reminder for appointment {appt.id}")

            await session.commit()
    finally:
        await evo_client.close()
        await engine.dispose()


@celery_app.task(name="expire_overdue_trials")
def expire_overdue_trials():
    """Daily task to suspend businesses whose dynamic free trial has expired without upgrading."""
    import asyncio
    asyncio.run(_async_expire_overdue_trials())


async def _async_expire_overdue_trials():
    now = datetime.now(timezone.utc)
    async with AsyncSessionLocal() as session:
        stmt = select(Business).where(
            and_(
                Business.subscription_status == "trial",
                Business.trial_ends_at.is_not(None),
                Business.trial_ends_at < now,
                Business.is_active.is_(True),
            )
        )
        expired = (await session.execute(stmt)).scalars().all()
        for biz in expired:
            biz.subscription_status = "trial_expired"
            logger.info(f"Marked overdue trial as trial_expired for business {biz.id}")
        await session.commit()
    await engine.dispose()


@celery_app.task(name="process_subscription_renewals")
def process_subscription_renewals():
    """Daily task to send Paymegate renewal links & authorizations for due/upcoming SaaS subscriptions."""
    import asyncio
    asyncio.run(_async_process_subscription_renewals())


async def _async_process_subscription_renewals():
    from decimal import Decimal
    from app.models.business import BusinessOwner
    from app.models.payment import Payment, PaymentMethod, PaymentStatus
    from app.models.saas import Plan
    from app.models.subscription import Subscription, SubscriptionStatus
    from app.integrations.payments.paymegate import PaymegateAdapter

    now = datetime.now(timezone.utc)
    due_window = now + timedelta(days=3)
    grace_cutoff = now - timedelta(days=3)

    evo_client = EvolutionAPIClient(base_url=settings.EVOLUTION_API_URL, api_key=settings.EVOLUTION_API_KEY)
    sender = WhatsAppMessageSender(evo_client)

    try:
        async with AsyncSessionLocal() as session:
            stmt = (
                select(Subscription, Business, Plan)
                .join(Business, Subscription.business_id == Business.id)
                .join(Plan, Subscription.plan_id == Plan.id)
                .where(
                    and_(
                        Subscription.status == SubscriptionStatus.active,
                        Subscription.current_period_end <= due_window,
                        Business.is_active.is_(True),
                    )
                )
            )
            rows = (await session.execute(stmt)).all()
            for sub, biz, plan in rows:
                if sub.current_period_end < grace_cutoff:
                    sub.status = SubscriptionStatus.past_due
                    biz.subscription_status = "past_due"
                    continue

                if not settings.PAYMEGATE_API_KEY:
                    continue

                owner = (
                    await session.execute(select(BusinessOwner).where(BusinessOwner.business_id == biz.id))
                ).scalars().first()
                branch = (
                    await session.execute(select(Branch).where(Branch.business_id == biz.id))
                ).scalars().first()

                renewal_payment = Payment(
                    business_id=biz.id,
                    appointment_id=None,
                    amount=float(plan.price),
                    currency="AZN",
                    method=PaymentMethod.paymegate,
                    status=PaymentStatus.pending,
                    notes=f"Subscription Renewal - {plan.name}",
                )
                session.add(renewal_payment)
                await session.flush()

                try:
                    link_res = await PaymegateAdapter().create_payment_link(
                        payment_id=renewal_payment.id,
                        amount=Decimal(str(plan.price)),
                        currency="AZN",
                        description=f"Randevu.vip {plan.name} Renewal",
                        merchant_config={
                            "business_id": str(biz.id),
                            "type": "saas_subscription",
                            "plan_id": str(plan.id),
                            "customer_email": owner.email if owner else "owner@randevu.vip",
                            "customer_name": owner.name if owner else biz.name,
                        },
                        return_url=f"https://app.{settings.PLATFORM_DOMAIN}/payments",
                    )
                    renewal_payment.gateway_transaction_id = link_res.transaction_id
                except Exception as exc:
                    logger.warning(f"Failed to generate renewal link for {biz.id}: {exc}")
                    continue

                due_date_str = sub.current_period_end.strftime("%Y-%m-%d")
                msg = (
                    f"Salam{(', ' + owner.name) if owner and owner.name else ''}! "
                    f"{biz.name} üçün Randevu.vip ({plan.name} - {plan.price} AZN) abunəliyinizin yenilənmə tarixi: {due_date_str}.\n"
                    f"Abunəliyi təsdiqləmək və ödəniş etmək üçün linkə keçid edin:\n{link_res.payment_url}"
                )

                if owner and owner.phone and branch:
                    instance_name = branch.whatsapp_instance_id or f"randevu_{str(biz.id)[:8]}_main"
                    await sender.send_response(instance_name=instance_name, to_phone=owner.phone, text=msg)

                if owner and owner.email and settings.RESEND_API_KEY:
                    import httpx
                    try:
                        async with httpx.AsyncClient(timeout=10.0) as client:
                            await client.post(
                                "https://api.resend.com/emails",
                                headers={
                                    "Authorization": f"Bearer {settings.RESEND_API_KEY}",
                                    "Content-Type": "application/json",
                                },
                                json={
                                    "from": settings.SMTP_FROM_EMAIL,
                                    "to": [owner.email],
                                    "subject": f"Randevu.vip — Abunəlik Yenilənməsi ({plan.name})",
                                    "html": f"<p>{msg.replace(chr(10), '<br>')}</p>",
                                },
                            )
                    except Exception:
                        pass

                logger.info(f"Sent subscription renewal checkout link to business {biz.id}")

            await session.commit()
    finally:
        await evo_client.close()
        await engine.dispose()
