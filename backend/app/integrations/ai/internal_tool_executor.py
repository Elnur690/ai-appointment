import logging
from uuid import UUID
from datetime import date as date_type, datetime, timedelta, timezone
from sqlalchemy import select, and_, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.integrations.ai.provider import ToolCall
from app.models.appointment import Appointment, AppointmentStatus
from app.models.business import Business
from app.models.customer import Customer
from app.models.saas import Plan
from app.models.service import Service
from app.models.staff import Staff
from app.models.subscription import Subscription
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
            'get_next_customer': self._get_next_customer,
            'get_today_schedule': self._get_today_schedule,
            'get_upcoming_appointments': self._get_upcoming_appointments,
            'get_daily_revenue_summary': self._get_daily_revenue_summary,
            'get_no_shows': self._get_no_shows,
            'get_subscription_status': self._get_subscription_status,
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

        if date:
            target_date = date_type.fromisoformat(date)
        else:
            target_date = datetime.now(timezone.utc).date()
        day_start = datetime.combine(target_date, datetime.min.time(), tzinfo=timezone.utc)
        day_end = day_start + timedelta(days=1)

        stmt = select(func.sum(Payment.amount)).where(
            and_(
                Payment.business_id == self.business_id,
                Payment.status == PaymentStatus.completed,
                Payment.created_at >= day_start,
                Payment.created_at < day_end,
            )
        )
        result = await self.db.execute(stmt)
        total = result.scalar() or 0
        return {'date': target_date.isoformat(), 'total_revenue': float(total), 'currency': 'AZN'}

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

    async def _get_next_customer(self) -> dict:
        now = datetime.now(timezone.utc)
        stmt = (
            select(Appointment, Customer, Service, Staff)
            .join(Customer, Appointment.customer_id == Customer.id)
            .join(Service, Appointment.service_id == Service.id)
            .join(Staff, Appointment.staff_id == Staff.id)
            .where(
                and_(
                    Appointment.business_id == self.business_id,
                    Appointment.start_time >= now,
                    Appointment.status.in_([AppointmentStatus.confirmed, AppointmentStatus.pending]),
                )
            )
            .order_by(Appointment.start_time.asc())
            .limit(1)
        )
        if self.scope == "single_branch" and self.branch_id:
            stmt = stmt.where(Appointment.branch_id == self.branch_id)
        row = (await self.db.execute(stmt)).first()
        if not row:
            return {'next_customer': None, 'message': 'No upcoming customers scheduled.'}
        appt, cust, svc, st = row
        return {
            'next_customer': {
                'customer_name': cust.name or cust.phone_number,
                'customer_phone': cust.phone_number,
                'service': svc.name,
                'staff': st.name,
                'start_time': appt.start_time.strftime('%Y-%m-%d %H:%M'),
                'status': appt.status.value,
            }
        }

    async def _get_subscription_status(self) -> dict:
        if self.sender_role != 'owner':
            return {'error': 'Subscription details are restricted to business owners.'}
        biz = (await self.db.execute(select(Business).where(Business.id == self.business_id))).scalar_one_or_none()
        if not biz:
            return {'error': 'Business not found'}
        plan = (await self.db.execute(select(Plan).where(Plan.id == biz.plan_id))).scalar_one_or_none() if biz.plan_id else None
        sub = (await self.db.execute(select(Subscription).where(Subscription.business_id == self.business_id))).scalars().first()
        return {
            'business_name': biz.name,
            'plan_name': plan.name if plan else 'Starter',
            'plan_price_azn': float(plan.price) if plan else 29.0,
            'subscription_status': biz.subscription_status or 'trial',
            'trial_ends_at': biz.trial_ends_at.strftime('%Y-%m-%d') if biz.trial_ends_at else None,
            'current_period_end': sub.current_period_end.strftime('%Y-%m-%d') if sub and sub.current_period_end else None,
            'ai_message_quota': int(plan.ai_message_quota) if plan else 1000,
        }

    async def _get_branch_summary(self, branch_id: str | None = None) -> dict:
        return {'status': 'active', 'business_id': str(self.business_id)}
