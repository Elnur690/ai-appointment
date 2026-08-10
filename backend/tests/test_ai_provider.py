import pytest
from app.integrations.ai.provider import (
    ToolParameter,
    ToolParameterType,
    ToolDefinition,
    ToolCall,
    AIMessage,
    AIResponse,
    FinishReason,
)
from app.integrations.ai.tools import get_customer_tools
from app.integrations.ai.prompts import build_customer_system_prompt

def test_tool_definition_types():
    param = ToolParameter(
        name="service_id",
        type=ToolParameterType.STRING,
        description="ID of requested service",
        required=True,
    )
    tool = ToolDefinition(
        name="check_availability",
        description="Check available slots",
        parameters=[param],
    )
    assert tool.name == "check_availability"
    assert tool.parameters[0].required is True

def test_customer_tools_list():
    tools = get_customer_tools()
    tool_names = [t.name for t in tools]
    assert "check_availability" in tool_names
    assert "create_appointment" in tool_names
    assert "reschedule_appointment" in tool_names
    assert "cancel_appointment" in tool_names
    assert "request_human_agent" in tool_names

def test_system_prompt_builder():
    prompt = build_customer_system_prompt(
        business_name="Beauty Studio Baku",
        business_description="Premium hair and nail salon",
        branch_name="Central Branch",
        working_hours={"monday": {"start": "09:00", "end": "18:00"}},
        timezone="Asia/Baku",
        services=[{"name": "Haircut", "duration_minutes": 45, "price": "30.00", "description": "Standard haircut"}],
        tone_config={"language": "az", "tone": "friendly", "greeting_style": "warm", "custom_instructions": "Offer tea on arrival"},
        current_datetime="2026-08-09T20:00:00",
    )
    assert "Beauty Studio Baku" in prompt
    assert "Haircut" in prompt
    assert "Asia/Baku" in prompt
    assert "Offer tea on arrival" in prompt
