import logging
from uuid import UUID
from datetime import date, datetime, timedelta, timezone
from sqlalchemy import select, and_, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.integrations.ai.provider import ToolCall
from app.models.appointment import Appointment, AppointmentStatus
from app.models.staff import Staff
from app.models.payment import Payment, PaymentStatus

logger = logging.getLogger(__name__)

class InternalGroupToolExecutor:
    """Executes read-only internal group tool calls with proper security scoping."""
    
    def __init__(
        self,
        db: AsyncSession,
        business_id: UUID,
        branch_id: UUID | None,
        sender_role: str,
        scope: str = "single_branch",
    ):
        self.db = db
        self.business_id = business_id
        self.branch_id = branch_id
        self.sender_role = sender_role  # 'owner' or 'staff'
        self.scope = scope  # 'single_branch' or 'all_branches'
    
    async def execute(self, tool_call: ToolCall) -> dict:
        handlers = {
            'get_today_schedule': self._get_today_schedule,
            'get_upcoming_appointments': self._get_upcoming_appointments,
            'get_daily_revenue_summary': self._get_daily_revenue_summary,
            'get_no_shows': self._get_no_shows,
            'get_branch_summary': self._get_branch_summary,
        }
        handler = handlers.get(tool_call.name)
        if not handler:
            return {'error': f'Unknown internal tool: {tool_call.name}'}
        
        try:
            return await handler(**tool_call.arguments)
        except Exception as e:
            logger.error(f"Error executing internal tool {tool_call.name}: {e}")
            return {'error': str(e)}

    async def _get_today_schedule(self, staff_id: str | None = None) -> dict:
        today_start = datetime.now(timezone.utc).replace(hour=0, minute=0, second=0, microsecond=0)
        today_end = today_start + timedelta(days=1)
        
        stmt = select(Appointment).where(
            and_(
                Appointment.business_id == self.business_id,
                Appointment.start_time >= today_start,
                Appointment.start_time < today_end,
                Appointment.status != AppointmentStatus.cancelled,
            )
        )
        if self.scope == "single_branch" and self.branch_id:
            stmt = stmt.where(Appointment.branch_id == self.branch_id)
            
        result = await self.db.execute(stmt)
        appointments = result.scalars().all()
        
        return {
            'date': today_start.strftime('%Y-%m-%d'),
            'total_appointments': len(appointments),
            'appointments': [
                {
                    'id': str(a.id),
                    'time': a.start_time.strftime('%H:%M'),
                    'status': a.status.value,
                }
                for a in appointments
            ]
        }

    async def _get_upcoming_appointments(self, days: int = 3, staff_id: str | None = None) -> dict:
        now = datetime.now(timezone.utc)
        future = now + timedelta(days=days)
        
        stmt = select(Appointment).where(
            and_(
                Appointment.business_id == self.business_id,
                Appointment.start_time >= now,
                Appointment.start_time <= future,
                Appointment.status == AppointmentStatus.confirmed,
            )
        )
        if self.scope == "single_branch" and self.branch_id:
            stmt = stmt.where(Appointment.branch_id == self.branch_id)
            
        result = await self.db.execute(stmt)
        appointments = result.scalars().all()
        return {'upcoming_count': len(appointments)}

    async def _get_daily_revenue_summary(self, date: str | None = None) -> dict:
        if self.sender_role != 'owner':
            return {'error': 'Revenue details are restricted to business owners.'}
        
        stmt = select(func.sum(Payment.amount)).where(
            and_(
                Payment.business_id == self.business_id,
                Payment.status == PaymentStatus.completed,
            )
        )
        result = await self.db.execute(stmt)
        total = result.scalar() or 0
        return {'total_revenue': float(total), 'currency': 'AZN'}

    async def _get_no_shows(self, days: int = 7) -> dict:
        since = datetime.now(timezone.utc) - timedelta(days=days)
        stmt = select(Appointment).where(
            and_(
                Appointment.business_id == self.business_id,
                Appointment.start_time >= since,
                Appointment.status == AppointmentStatus.no_show,
            )
        )
        result = await self.db.execute(stmt)
        no_shows = result.scalars().all()
        return {'no_show_count': len(no_shows)}

    async def _get_branch_summary(self, branch_id: str | None = None) -> dict:
        return {'status': 'active', 'business_id': str(self.business_id)}
