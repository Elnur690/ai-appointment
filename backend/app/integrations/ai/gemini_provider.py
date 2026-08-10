import asyncio
import time
from typing import Any
from google import genai
from google.genai import types

from app.integrations.ai.provider import (
    AIProvider,
    AIMessage,
    AIResponse,
    ToolDefinition,
    ToolParameter,
    ToolCall,
    FinishReason,
    TokenUsage,
)

class GeminiProvider(AIProvider):
    """Gemini API provider implementation."""

    def __init__(
        self,
        api_key: str,
        model_name: str = "gemini-3.5-flash",
        max_rpm: int = 60,
        max_rpd: int = 1500,
    ):
        self.client = genai.Client(api_key=api_key)
        self.model_name = model_name
        self.max_rpm = max_rpm
        self.max_rpd = max_rpd
        
        # Simple token bucket for rate limiting
        self._lock = asyncio.Lock()
        self._tokens = max_rpm
        self._last_refill = time.monotonic()

    async def _wait_for_rate_limit(self):
        async with self._lock:
            now = time.monotonic()
            elapsed = now - self._last_refill
            
            # Refill tokens
            refill_amount = int(elapsed * (self.max_rpm / 60.0))
            if refill_amount > 0:
                self._tokens = min(self.max_rpm, self._tokens + refill_amount)
                self._last_refill = now
            
            if self._tokens <= 0:
                # Wait for 1 token
                wait_time = 60.0 / self.max_rpm
                await asyncio.sleep(wait_time)
                self._tokens = 1
                self._last_refill = time.monotonic()
            
            self._tokens -= 1

    def _build_parameter_schema(self, params: list[ToolParameter]) -> dict:
        schema_props = {}
        required = []
        for p in params:
            prop = {"type": p.type.value.upper()}
            if p.description:
                prop["description"] = p.description
            if p.enum:
                prop["enum"] = p.enum
            if p.items:
                prop["items"] = p.items
            if p.properties:
                prop["properties"] = p.properties
                
            schema_props[p.name] = prop
            if p.required:
                required.append(p.name)
                
        return {
            "type": "OBJECT",
            "properties": schema_props,
            "required": required,
        }

    def _convert_tools_to_declarations(self, tools: list[ToolDefinition]) -> list[types.FunctionDeclaration]:
        declarations = []
        for t in tools:
            schema = self._build_parameter_schema(t.parameters)
            declarations.append(
                types.FunctionDeclaration(
                    name=t.name,
                    description=t.description,
                    parameters=schema,
                )
            )
        return declarations

    def _convert_messages_to_contents(self, messages: list[AIMessage]) -> list[types.Content]:
        contents = []
        for msg in messages:
            if msg.role == "user":
                contents.append(types.Content(role="user", parts=[types.Part.from_text(msg.content)]))
            elif msg.role == "assistant":
                parts = []
                if msg.content:
                    parts.append(types.Part.from_text(msg.content))
                if msg.tool_calls:
                    for tc in msg.tool_calls:
                        parts.append(types.Part.from_function_call(name=tc.name, args=tc.arguments))
                contents.append(types.Content(role="model", parts=parts))
            elif msg.role == "tool":
                if msg.content:
                    import json
                    try:
                        response_dict = json.loads(msg.content)
                    except json.JSONDecodeError:
                        response_dict = {"result": msg.content}
                else:
                    response_dict = {}
                    
                contents.append(
                    types.Content(
                        role="user",
                        parts=[
                            types.Part.from_function_response(
                                name=msg.tool_name or "unknown",
                                response=response_dict
                            )
                        ]
                    )
                )
        return contents

    def _parse_response(self, response: Any) -> AIResponse:
        candidate = response.candidates[0]
        text = None
        tool_calls = []
        
        if candidate.content and candidate.content.parts:
            for part in candidate.content.parts:
                if part.text:
                    text = (text or "") + part.text
                elif part.function_call:
                    import uuid
                    tool_calls.append(
                        ToolCall(
                            id=str(uuid.uuid4()),
                            name=part.function_call.name,
                            arguments=dict(part.function_call.args) if part.function_call.args else {}
                        )
                    )
                    
        finish_reason = FinishReason.STOP
        if candidate.finish_reason == types.FinishReason.STOP:
            finish_reason = FinishReason.STOP
        elif candidate.finish_reason == types.FinishReason.MAX_TOKENS:
            finish_reason = FinishReason.MAX_TOKENS
        elif candidate.finish_reason == types.FinishReason.SAFETY:
            finish_reason = FinishReason.SAFETY
        elif candidate.finish_reason == types.FinishReason.OTHER:
            finish_reason = FinishReason.ERROR
            
        if not finish_reason and tool_calls:
             finish_reason = FinishReason.TOOL_CALL

        usage = None
        if response.usage_metadata:
            usage = TokenUsage(
                prompt_tokens=response.usage_metadata.prompt_token_count,
                completion_tokens=response.usage_metadata.candidates_token_count,
                total_tokens=response.usage_metadata.total_token_count,
            )

        return AIResponse(
            text=text,
            tool_calls=tool_calls,
            finish_reason=finish_reason,
            usage=usage,
            raw_response=response,
        )

    async def generate_response(
        self,
        messages: list[AIMessage],
        system_prompt: str,
        tools: list[ToolDefinition] | None = None,
        temperature: float = 0.7,
        max_tokens: int | None = None,
    ) -> AIResponse:
        await self._wait_for_rate_limit()
        
        contents = self._convert_messages_to_contents(messages)
        
        gemini_tools = None
        if tools:
            declarations = self._convert_tools_to_declarations(tools)
            gemini_tools = [types.Tool(function_declarations=declarations)]
            
        config = types.GenerateContentConfig(
            system_instruction=system_prompt,
            temperature=temperature,
            max_output_tokens=max_tokens,
            tools=gemini_tools,
            automatic_function_calling=types.AutomaticFunctionCallingConfig(disable=True) if gemini_tools else None,
        )
        
        try:
            # We use asyncio.to_thread because the genai Client might be synchronous
            response = await asyncio.to_thread(
                self.client.models.generate_content,
                model=self.model_name,
                contents=contents,
                config=config,
            )
            return self._parse_response(response)
        except Exception as e:
            return AIResponse(
                text=f"Error communicating with AI provider: {str(e)}",
                finish_reason=FinishReason.ERROR,
            )

    async def health_check(self) -> bool:
        try:
            await self._wait_for_rate_limit()
            response = await asyncio.to_thread(
                self.client.models.generate_content,
                model=self.model_name,
                contents=[types.Content(role="user", parts=[types.Part.from_text("ping")])],
            )
            return bool(response.text)
        except Exception:
            return False
