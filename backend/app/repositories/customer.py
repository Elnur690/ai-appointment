from uuid import UUID
from sqlalchemy import select
from app.repositories.base import BaseRepository
from app.models.customer import Customer

class CustomerRepository(BaseRepository[Customer]):
    def __init__(self, session, business_id: UUID | None = None):
        super().__init__(Customer, session, business_id)
        
    async def get_by_phone(self, business_id: UUID, phone: str) -> Customer | None:
        stmt = select(Customer).where(
            Customer.business_id == business_id,
            Customer.phone_number == phone
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()
        
    async def get_or_create_by_phone(self, business_id: UUID, phone: str, name: str = None) -> Customer:
        customer = await self.get_by_phone(business_id, phone)
        if not customer:
            customer = Customer(
                business_id=business_id,
                phone_number=phone,
                name=name
            )
            self.session.add(customer)
            await self.session.flush()
        return customer
