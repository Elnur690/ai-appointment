from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any
from enum import Enum

class ToolParameterType(str, Enum):
    STRING = "string"
    INTEGER = "integer"
    NUMBER = "number"
    BOOLEAN = "boolean"
    ARRAY = "array"
    OBJECT = "object"

@dataclass
class ToolParameter:
    name: str
    type: ToolParameterType
    description: str
    required: bool = True
    enum: list[str] | None = None
    items: dict | None = None  # for array types
    properties: dict | None = None  # for object types

@dataclass
class ToolDefinition:
    name: str
    description: str
    parameters: list[ToolParameter]

@dataclass
class ToolCall:
    id: str
    name: str
    arguments: dict[str, Any]

@dataclass
class AIMessage:
    role: str  # 'user', 'assistant', 'tool'
    content: str | None = None
    tool_calls: list[ToolCall] | None = None
    tool_call_id: str | None = None  # for tool response messages
    tool_name: str | None = None  # for tool response messages

class FinishReason(str, Enum):
    STOP = "stop"
    TOOL_CALL = "tool_call"
    MAX_TOKENS = "max_tokens"
    ERROR = "error"
    SAFETY = "safety"

@dataclass
class TokenUsage:
    prompt_tokens: int = 0
    completion_tokens: int = 0
    total_tokens: int = 0

@dataclass
class AIResponse:
    text: str | None
    tool_calls: list[ToolCall] = field(default_factory=list)
    finish_reason: FinishReason = FinishReason.STOP
    usage: TokenUsage | None = None
    raw_response: Any = None  # provider-specific response for debugging

class AIProvider(ABC):
    """Abstract base class for AI providers. All conversation logic operates on these types."""
    
    @abstractmethod
    async def generate_response(
        self,
        messages: list[AIMessage],
        system_prompt: str,
        tools: list[ToolDefinition] | None = None,
        temperature: float = 0.7,
        max_tokens: int | None = None,
    ) -> AIResponse:
        """Generate a response from the AI model."""
        ...
    
    @abstractmethod
    async def health_check(self) -> bool:
        """Check if the provider is available."""
        ...
