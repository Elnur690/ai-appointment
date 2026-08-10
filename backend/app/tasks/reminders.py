import logging
from datetime import datetime, timedelta, timezone
from sqlalchemy import select, and_
from app.tasks.celery_app import celery_app
from app.core.database import AsyncSessionLocal
from app.models.appointment import Appointment, AppointmentStatus
from app.integrations.whatsapp.client import EvolutionAPIClient
from app.integrations.whatsapp.message_sender import WhatsAppMessageSender
from app.core.config import settings

logger = logging.getLogger(__name__)

@celery_app.task(name="send_appointment_reminders")
def send_appointment_reminders():
    """Celery Beat task running every 5 minutes to send 24h and 2h appointment reminders."""
    import asyncio
    asyncio.run(_async_send_reminders())

async def _async_send_reminders():
    now = datetime.now(timezone.utc)
    
    # 24h window: 23h55m to 24h05m
    window_24h_start = now + timedelta(hours=23, minutes=55)
    window_24h_end = now + timedelta(hours=24, minutes=5)
    
    # 2h window: 1h55m to 2h05m
    window_2h_start = now + timedelta(hours=1, minutes=55)
    window_2h_end = now + timedelta(hours=2, minutes=5)
    
    async with AsyncSessionLocal() as session:
        # Query 24h reminders due
        stmt_24h = select(Appointment).where(
            and_(
                Appointment.status == AppointmentStatus.confirmed,
                Appointment.start_time >= window_24h_start,
                Appointment.start_time <= window_24h_end,
                Appointment.reminder_24h_sent_at.is_(None),
            )
        )
        res_24h = await session.execute(stmt_24h)
        reminders_24h = res_24h.scalars().all()
        
        for appt in reminders_24h:
            appt.reminder_24h_sent_at = now
            logger.info(f"Dispatched 24h reminder for appointment {appt.id}")
            
        # Query 2h reminders due
        stmt_2h = select(Appointment).where(
            and_(
                Appointment.status == AppointmentStatus.confirmed,
                Appointment.start_time >= window_2h_start,
                Appointment.start_time <= window_2h_end,
                Appointment.reminder_2h_sent_at.is_(None),
            )
        )
        res_2h = await session.execute(stmt_2h)
        reminders_2h = res_2h.scalars().all()
        
        for appt in reminders_2h:
            appt.reminder_2h_sent_at = now
            logger.info(f"Dispatched 2h reminder for appointment {appt.id}")
            
        await session.commit()
