from uuid import UUID
from sqlalchemy import select
from app.repositories.base import BaseRepository
from app.models.staff import Staff, StaffSchedule, StaffService

class StaffRepository(BaseRepository[Staff]):
    def __init__(self, session, business_id: UUID | None = None):
        super().__init__(Staff, session, business_id)
        
    async def get_by_branch_id(self, branch_id: UUID) -> list[Staff]:
        stmt = self._scoped_query().where(Staff.branch_id == branch_id)
        result = await self.session.execute(stmt)
        return list(result.scalars().all())
        
    async def get_by_email(self, email: str) -> Staff | None:
        stmt = self._scoped_query().where(Staff.email == email)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()
        
    async def get_active_by_branch(self, branch_id: UUID) -> list[Staff]:
        stmt = self._scoped_query().where(Staff.branch_id == branch_id, Staff.is_active == True)
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

class StaffScheduleRepository(BaseRepository[StaffSchedule]):
    def __init__(self, session, business_id: UUID | None = None):
        super().__init__(StaffSchedule, session, business_id)
        
    async def get_by_staff_id(self, staff_id: UUID) -> list[StaffSchedule]:
        stmt = self._scoped_query().where(StaffSchedule.staff_id == staff_id)
        result = await self.session.execute(stmt)
        return list(result.scalars().all())
        
    async def get_by_staff_and_day(self, staff_id: UUID, day_of_week: int) -> StaffSchedule | None:
        stmt = self._scoped_query().where(
            StaffSchedule.staff_id == staff_id,
            StaffSchedule.day_of_week == day_of_week
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()
        
    async def bulk_upsert_schedules(self, schedules: list[StaffSchedule]) -> list[StaffSchedule]:
        # Basic implementation for bulk upsert
        for schedule in schedules:
            existing = await self.get_by_staff_and_day(schedule.staff_id, schedule.day_of_week)
            if existing:
                existing.start_time = schedule.start_time
                existing.end_time = schedule.end_time
            else:
                self.session.add(schedule)
        await self.session.flush()
        return schedules

class StaffServiceRepository(BaseRepository[StaffService]):
    def __init__(self, session, business_id: UUID | None = None):
        super().__init__(StaffService, session, business_id)
        
    async def get_by_staff_id(self, staff_id: UUID) -> list[StaffService]:
        stmt = self._scoped_query().where(StaffService.staff_id == staff_id)
        result = await self.session.execute(stmt)
        return list(result.scalars().all())
        
    async def get_staff_for_service(self, service_id: UUID) -> list[StaffService]:
        stmt = self._scoped_query().where(StaffService.service_id == service_id)
        result = await self.session.execute(stmt)
        return list(result.scalars().all())
