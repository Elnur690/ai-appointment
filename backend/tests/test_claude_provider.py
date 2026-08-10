import pytest
from app.integrations.ai.claude_provider import ClaudeProvider
from app.integrations.ai.provider import ToolDefinition, ToolParameter, ToolParameterType, AIMessage

def test_claude_tool_conversion():
    provider = ClaudeProvider(api_key="mock_key")
    param = ToolParameter(name="date", type=ToolParameterType.STRING, description="Target date", required=True)
    tool = ToolDefinition(name="check_availability", description="Check available slots", parameters=[param])
    
    converted = provider._convert_tool(tool)
    assert converted["name"] == "check_availability"
    assert "input_schema" in converted
    assert "date" in converted["input_schema"]["properties"]

def test_claude_response_parser():
    provider = ClaudeProvider(api_key="mock_key")
    mock_data = {
        "content": [
            {"type": "text", "text": "I can help you book an appointment."},
            {"type": "tool_use", "id": "call_1", "name": "check_availability", "input": {"date": "2026-08-15"}}
        ],
        "usage": {"input_tokens": 120, "output_tokens": 40}
    }
    response = provider._parse_response(mock_data)
    assert response.text == "I can help you book an appointment."
    assert len(response.tool_calls) == 1
    assert response.tool_calls[0].name == "check_availability"
    assert response.usage.total_tokens == 160
