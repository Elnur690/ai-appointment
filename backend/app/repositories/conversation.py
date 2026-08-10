from uuid import UUID
from sqlalchemy import select
from app.repositories.base import BaseRepository
from app.models.conversation import Conversation, Message

class ConversationRepository(BaseRepository[Conversation]):
    def __init__(self, session, business_id: UUID | None = None):
        super().__init__(Conversation, session, business_id)
        
    async def get_by_customer_and_branch(self, customer_id: UUID, branch_id: UUID) -> Conversation | None:
        stmt = self._scoped_query().where(
            Conversation.customer_id == customer_id,
            Conversation.branch_id == branch_id
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()
        
    async def get_or_create_for_customer(self, customer_id: UUID, branch_id: UUID, business_id: UUID) -> Conversation:
        conversation = await self.get_by_customer_and_branch(customer_id, branch_id)
        if not conversation:
            conversation = Conversation(
                business_id=business_id,
                customer_id=customer_id,
                branch_id=branch_id,
                ai_active=True
            )
            self.session.add(conversation)
            await self.session.flush()
        return conversation
        
    async def get_active_conversations(self, branch_id: UUID) -> list[Conversation]:
        stmt = self._scoped_query().where(
            Conversation.branch_id == branch_id,
            Conversation.ai_active == True
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())
        
    async def update_ai_active(self, conversation_id: UUID, ai_active: bool) -> Conversation | None:
        conversation = await self.get_by_id(conversation_id)
        if conversation:
            conversation.ai_active = ai_active
            await self.session.flush()
        return conversation

class MessageRepository(BaseRepository[Message]):
    def __init__(self, session, business_id: UUID | None = None):
        super().__init__(Message, session, business_id)
        
    async def get_by_conversation(self, conversation_id: UUID, limit: int = 50, offset: int = 0) -> list[Message]:
        stmt = self._scoped_query().where(
            Message.conversation_id == conversation_id
        ).order_by(Message.created_at.desc()).offset(offset).limit(limit)
        result = await self.session.execute(stmt)
        return list(result.scalars().all())
        
    async def get_recent_messages(self, conversation_id: UUID, limit: int = 20) -> list[Message]:
        messages = await self.get_by_conversation(conversation_id, limit=limit)
        return list(reversed(messages))  # Return in chronological order
        
    async def create_message(self, message: Message) -> Message:
        return await self.create(message)
