import logging
from typing import Any
import httpx
from app.integrations.ai.provider import (
    AIProvider,
    AIMessage,
    AIResponse,
    ToolDefinition,
    ToolCall,
    FinishReason,
    TokenUsage,
)

logger = logging.getLogger(__name__)

class ClaudeProvider(AIProvider):
    """Claude AI Provider implementing AIProvider abstraction via Anthropic API."""
    
    BASE_URL = "https://api.anthropic.com/v1/messages"
    
    def __init__(self, api_key: str, model_name: str = "claude-3-5-sonnet-20241022"):
        self.api_key = api_key
        self.model_name = model_name
    
    async def generate_response(
        self,
        messages: list[AIMessage],
        system_prompt: str,
        tools: list[ToolDefinition] | None = None,
        temperature: float = 0.7,
        max_tokens: int | None = 1024,
    ) -> AIResponse:
        headers = {
            "x-api-key": self.api_key,
            "anthropic-version": "2023-06-01",
            "content-type": "application/json",
        }
        
        # Convert internal messages to Claude format
        claude_messages = []
        for msg in messages:
            if msg.role in ["user", "assistant"]:
                claude_messages.append({"role": msg.role, "content": msg.content or ""})
        
        payload: dict[str, Any] = {
            "model": self.model_name,
            "system": system_prompt,
            "messages": claude_messages,
            "max_tokens": max_tokens or 1024,
            "temperature": temperature,
        }
        
        if tools:
            payload["tools"] = [self._convert_tool(t) for t in tools]
            
        async with httpx.AsyncClient(timeout=30.0) as client:
            try:
                resp = await client.post(self.BASE_URL, json=payload, headers=headers)
                data = resp.json()
                return self._parse_response(data)
            except Exception as e:
                logger.error(f"Claude API request failed: {e}")
                return AIResponse(text="API error occurred", finish_reason=FinishReason.ERROR)

    async def health_check(self) -> bool:
        return bool(self.api_key)

    def _convert_tool(self, tool: ToolDefinition) -> dict:
        properties = {}
        required = []
        for param in tool.parameters:
            properties[param.name] = {"type": param.type.value, "description": param.description}
            if param.required:
                required.append(param.name)
        return {
            "name": tool.name,
            "description": tool.description,
            "input_schema": {
                "type": "object",
                "properties": properties,
                "required": required,
            },
        }

    def _parse_response(self, data: dict) -> AIResponse:
        content_blocks = data.get("content", [])
        text_content = ""
        tool_calls = []
        
        for block in content_blocks:
            if block.get("type") == "text":
                text_content += block.get("text", "")
            elif block.get("type") == "tool_use":
                tool_calls.append(
                    ToolCall(
                        id=block.get("id", ""),
                        name=block.get("name", ""),
                        arguments=block.get("input", {}),
                    )
                )
                
        finish_reason = FinishReason.TOOL_CALL if tool_calls else FinishReason.STOP
        usage_data = data.get("usage", {})
        usage = TokenUsage(
            prompt_tokens=usage_data.get("input_tokens", 0),
            completion_tokens=usage_data.get("output_tokens", 0),
            total_tokens=usage_data.get("input_tokens", 0) + usage_data.get("output_tokens", 0),
        )
        return AIResponse(text=text_content or None, tool_calls=tool_calls, finish_reason=finish_reason, usage=usage, raw_response=data)
