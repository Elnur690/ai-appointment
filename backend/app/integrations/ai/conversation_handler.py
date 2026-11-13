import json
from dataclasses import dataclass
from datetime import datetime, timezone
from uuid import UUID
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.integrations.ai.provider import AIProvider, AIMessage, FinishReason
from app.integrations.ai.tools import get_customer_tools
from app.integrations.ai.tool_executor import ToolExecutor
from app.integrations.ai.prompts import build_customer_system_prompt
from app.models.business import Business, Branch
from app.models.customer import Customer
from app.models.conversation import Conversation, Message, MessageDirection
from app.models.service import Service


@dataclass
class ConversationResult:
    response_text: str | None
    ai_active: bool
    human_handoff_requested: bool
    tool_calls_made: list[str]
    error: str | None = None


class ConversationHandler:
    """Orchestrates AI-powered conversations backed by PostgreSQL."""

    MAX_TOOL_ITERATIONS = 5

    def __init__(
        self,
        ai_provider: AIProvider,
        db: AsyncSession,
        branch_id: UUID,
        business_id: UUID,
    ):
        self.ai_provider = ai_provider
        self.db = db
        self.branch_id = branch_id
        self.business_id = business_id

    async def handle_customer_message(
        self,
        message_text: str,
        customer_phone: str,
        customer_name: str | None = None,
    ) -> ConversationResult:
        # 1. Load or create Customer
        cust = (
            await self.db.execute(
                select(Customer).where(
                    Customer.business_id == self.business_id,
                    Customer.phone_number == customer_phone,
                )
            )
        ).scalar_one_or_none()
        if not cust:
            cust = Customer(
                business_id=self.business_id,
                phone_number=customer_phone,
                name=customer_name or customer_phone,
            )
            self.db.add(cust)
            await self.db.flush()

        # 2. Load or create Conversation
        conv = (
            await self.db.execute(
                select(Conversation).where(
                    Conversation.business_id == self.business_id,
                    Conversation.customer_id == cust.id,
                )
            )
        ).scalars().first()
        if not conv:
            conv = Conversation(
                business_id=self.business_id,
                branch_id=self.branch_id,
                customer_id=cust.id,
                ai_active=True,
                last_message_at=datetime.now(timezone.utc),
            )
            self.db.add(conv)
            await self.db.flush()

        # 3. Save inbound user message
        in_msg = Message(
            conversation_id=conv.id,
            direction=MessageDirection.inbound,
            sender_role="customer",
            content=message_text,
            message_type="text",
        )
        self.db.add(in_msg)
        conv.last_message_at = datetime.now(timezone.utc)
        await self.db.flush()

        ai_active = bool(conv.ai_active)
        if not ai_active:
            return ConversationResult(
                response_text=None,
                ai_active=False,
                human_handoff_requested=False,
                tool_calls_made=[],
            )

        # 4. Load recent conversation history from DB
        hist_rows = (
            await self.db.execute(
                select(Message)
                .where(Message.conversation_id == conv.id, Message.id != in_msg.id)
                .order_by(Message.created_at.desc())
                .limit(10)
            )
        ).scalars().all()
        history: list[AIMessage] = [
            AIMessage(
                role="user" if m.direction == MessageDirection.inbound else "assistant",
                content=m.content,
            )
            for m in reversed(hist_rows)
        ]

        # 5. Load real Business, Branch, and Services from PostgreSQL
        biz = (
            await self.db.execute(select(Business).where(Business.id == self.business_id))
        ).scalar_one_or_none()
        branch = (
            await self.db.execute(select(Branch).where(Branch.id == self.branch_id))
        ).scalar_one_or_none()
        srv_rows = (
            await self.db.execute(
                select(Service).where(Service.business_id == self.business_id, Service.is_active == True)
            )
        ).scalars().all()

        system_prompt = build_customer_system_prompt(
            business_name=biz.name if biz else "Business",
            business_description=(biz.description or "") if biz else "",
            branch_name=branch.name if branch else "Main Branch",
            working_hours=(branch.working_hours if branch and branch.working_hours else {"monday": "09:00-18:00"}),
            timezone=(branch.timezone if branch else "Asia/Baku"),
            services=[
                {
                    "name": s.name,
                    "duration": s.duration_minutes,
                    "price": f"{float(s.price):.2f} {getattr(s, 'currency', 'AZN')}",
                    "description": s.description or "",
                }
                for s in srv_rows
            ],
            tone_config=(biz.default_ai_tone_config or {}) if biz else {},
            current_datetime=datetime.now(timezone.utc).isoformat(),
        )

        tools = get_customer_tools()
        tool_executor = ToolExecutor(self.db, self.branch_id, self.business_id, cust.id)

        messages = history + [AIMessage(role="user", content=message_text)]

        tool_calls_made: list[str] = []
        human_handoff_requested = False

        for _ in range(self.MAX_TOOL_ITERATIONS):
            try:
                response = await self.ai_provider.generate_response(
                    messages=messages,
                    system_prompt=system_prompt,
                    tools=tools,
                )
            except Exception as e:
                return ConversationResult(
                    response_text="Sorry, I am having trouble processing your request right now.",
                    ai_active=ai_active,
                    human_handoff_requested=human_handoff_requested,
                    tool_calls_made=tool_calls_made,
                    error=str(e),
                )

            ai_msg = AIMessage(
                role="assistant",
                content=response.text,
                tool_calls=response.tool_calls,
            )
            messages.append(ai_msg)

            if response.finish_reason == FinishReason.TOOL_CALL and response.tool_calls:
                for tc in response.tool_calls:
                    tool_calls_made.append(tc.name)
                    if tc.name == "request_human_agent":
                        human_handoff_requested = True
                        conv.ai_active = False

                    tool_result = await tool_executor.execute(tc)
                    tool_msg = AIMessage(
                        role="tool",
                        content=json.dumps(tool_result),
                        tool_call_id=tc.id,
                        tool_name=tc.name,
                    )
                    messages.append(tool_msg)
            else:
                break

        final_text = messages[-1].content if messages[-1].role == "assistant" else None
        if final_text:
            out_msg = Message(
                conversation_id=conv.id,
                direction=MessageDirection.outbound,
                sender_role="ai",
                content=final_text,
                message_type="text",
            )
            self.db.add(out_msg)
            await self.db.flush()

        return ConversationResult(
            response_text=final_text,
            ai_active=bool(conv.ai_active),
            human_handoff_requested=human_handoff_requested,
            tool_calls_made=tool_calls_made,
        )
