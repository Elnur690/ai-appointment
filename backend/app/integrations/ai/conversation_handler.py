import json
from dataclasses import dataclass
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Any

from app.integrations.ai.provider import AIProvider, AIMessage, FinishReason
from app.integrations.ai.tools import get_customer_tools
from app.integrations.ai.tool_executor import ToolExecutor
from app.integrations.ai.prompts import build_customer_system_prompt

@dataclass
class ConversationResult:
    response_text: str | None
    ai_active: bool
    human_handoff_requested: bool
    tool_calls_made: list[str]
    error: str | None = None

class ConversationHandler:
    """Orchestrates AI-powered conversations."""
    
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
        # TODO: Load or create Conversation record
        # TODO: Load or create Customer record
        customer_id = None
        
        # TODO: Check if ai_active — if not, skip AI and just save message
        ai_active = True
        
        if not ai_active:
            return ConversationResult(
                response_text=None,
                ai_active=False,
                human_handoff_requested=False,
                tool_calls_made=[]
            )

        # TODO: Load conversation history from DB (last N messages)
        # Mocking history for now
        history: list[AIMessage] = []
        
        # TODO: Load business/branch config for system prompt
        system_prompt = build_customer_system_prompt(
            business_name="Mock Business",
            business_description="A great place.",
            branch_name="Main Branch",
            working_hours={"monday": "9:00-17:00"},
            timezone="UTC",
            services=[{"name": "Mock Service", "duration": 30, "price": "$10", "description": "Mock desc"}],
            tone_config={},
            current_datetime="2026-08-09T12:00:00Z"
        )
        
        tools = get_customer_tools()
        tool_executor = ToolExecutor(self.db, self.branch_id, self.business_id, customer_id)
        
        messages = history + [AIMessage(role="user", content=message_text)]
        
        tool_calls_made = []
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
                    error=str(e)
                )

            # Add AI's message to the conversation
            ai_msg = AIMessage(
                role="assistant",
                content=response.text,
                tool_calls=response.tool_calls
            )
            messages.append(ai_msg)
            
            # TODO: Save AI response message to DB
            
            if response.finish_reason == FinishReason.TOOL_CALL and response.tool_calls:
                for tc in response.tool_calls:
                    tool_calls_made.append(tc.name)
                    if tc.name == "request_human_agent":
                        human_handoff_requested = True
                        
                    tool_result = await tool_executor.execute(tc)
                    
                    tool_msg = AIMessage(
                        role="tool",
                        content=json.dumps(tool_result),
                        tool_call_id=tc.id,
                        tool_name=tc.name
                    )
                    messages.append(tool_msg)
                    # TODO: Save tool response message to DB
            else:
                break
                
        return ConversationResult(
            response_text=messages[-1].content if messages[-1].role == "assistant" else None,
            ai_active=ai_active,
            human_handoff_requested=human_handoff_requested,
            tool_calls_made=tool_calls_made
        )
