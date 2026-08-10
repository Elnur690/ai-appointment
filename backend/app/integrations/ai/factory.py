import logging
from app.core.config import settings
from app.integrations.ai.provider import AIProvider
from app.integrations.ai.gemini_provider import GeminiProvider
from app.integrations.ai.claude_provider import ClaudeProvider
from app.integrations.ai.openai_provider import OpenAIProvider

from app.services.ai_registry import AIRegistryService

logger = logging.getLogger(__name__)

class AIProviderFactory:
    """Factory to instantiate and return the active AI provider via Zero-Downtime AIRegistryService."""

    @staticmethod
    def get_provider(
        selected_provider: str = "gemini",
        allowed_providers: list[str] | None = None,
        gemini_api_key: str | None = None,
        claude_api_key: str | None = None,
        openai_api_key: str | None = None,
    ) -> AIProvider:
        if gemini_api_key:
            AIRegistryService.update_provider_config("gemini", api_key=gemini_api_key)
        if claude_api_key:
            AIRegistryService.update_provider_config("claude", api_key=claude_api_key)
        if openai_api_key:
            AIRegistryService.update_provider_config("openai", api_key=openai_api_key)

        return AIRegistryService.get_active_provider(
            selected_provider=selected_provider,
            allowed_providers=allowed_providers,
        )

