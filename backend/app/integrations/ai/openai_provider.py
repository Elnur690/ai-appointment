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

class OpenAIProvider(AIProvider):
    """OpenAI AI Provider implementing AIProvider abstraction."""
    
    BASE_URL = "https://api.openai.com/v1/chat/completions"
    
    def __init__(self, api_key: str, model_name: str = "gpt-4o"):
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
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }
        
        openai_messages = [{"role": "system", "content": system_prompt}]
        for msg in messages:
            if msg.role in ["user", "assistant"]:
                openai_messages.append({"role": msg.role, "content": msg.content or ""})
        
        payload: dict[str, Any] = {
            "model": self.model_name,
            "messages": openai_messages,
            "temperature": temperature,
        }
        if max_tokens:
            payload["max_tokens"] = max_tokens
        if tools:
            payload["tools"] = [self._convert_tool(t) for t in tools]
            
        async with httpx.AsyncClient(timeout=30.0) as client:
            try:
                resp = await client.post(self.BASE_URL, json=payload, headers=headers)
                data = resp.json()
                return self._parse_response(data)
            except Exception as e:
                logger.error(f"OpenAI API request failed: {e}")
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
            "type": "function",
            "function": {
                "name": tool.name,
                "description": tool.description,
                "parameters": {
                    "type": "object",
                    "properties": properties,
                    "required": required,
                },
            },
        }

    def _parse_response(self, data: dict) -> AIResponse:
        choices = data.get("choices", [])
        if not choices:
            return AIResponse(text=None, finish_reason=FinishReason.ERROR)
        
        message = choices[0].get("message", {})
        text_content = message.get("content")
        tool_calls = []
        
        for tc in message.get("tool_calls", []):
            fn = tc.get("function", {})
            import json
            args = json.loads(fn.get("arguments", "{}"))
            tool_calls.append(ToolCall(id=tc.get("id", ""), name=fn.get("name", ""), arguments=args))
            
        finish_reason = FinishReason.TOOL_CALL if tool_calls else FinishReason.STOP
        usage_data = data.get("usage", {})
        usage = TokenUsage(
            prompt_tokens=usage_data.get("prompt_tokens", 0),
            completion_tokens=usage_data.get("completion_tokens", 0),
            total_tokens=usage_data.get("total_tokens", 0),
        )
        return AIResponse(text=text_content, tool_calls=tool_calls, finish_reason=finish_reason, usage=usage, raw_response=data)
