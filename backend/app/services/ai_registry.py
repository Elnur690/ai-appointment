import logging
from app.core.config import settings
from app.integrations.ai.provider import AIProvider
from app.integrations.ai.gemini_provider import GeminiProvider
from app.integrations.ai.claude_provider import ClaudeProvider
from app.integrations.ai.openai_provider import OpenAIProvider

logger = logging.getLogger(__name__)

class AIRegistryService:
    """
    Zero-Downtime Hot-Swappable AI Registry & Key Vault.
    Allows live model version upgrades & API key rotation without server restarts or downtime.
    """

    # In-memory dynamic model registry (updatable live via SaaS Admin API)
    MODEL_REGISTRY = {
        "gemini": {"model_name": "gemini-3.5-flash", "api_key": None},
        "claude": {"model_name": "claude-3-7-sonnet", "api_key": None},
        "openai": {"model_name": "gpt-4o", "api_key": None},
    }

    @classmethod
    def update_provider_config(cls, provider: str, model_name: str | None = None, api_key: str | None = None):
        """Update provider model version or API key live with zero downtime."""
        provider = provider.lower()
        if provider in cls.MODEL_REGISTRY:
            if model_name:
                cls.MODEL_REGISTRY[provider]["model_name"] = model_name
                logger.info(f"AIRegistry: Updated '{provider}' model version to '{model_name}'.")
            if api_key:
                cls.MODEL_REGISTRY[provider]["api_key"] = api_key
                logger.info(f"AIRegistry: Rotated API key for '{provider}'.")

    @classmethod
    def get_provider_config(cls, provider: str) -> dict:
        """Get live model string and key for provider."""
        return cls.MODEL_REGISTRY.get(provider.lower(), {"model_name": "gemini-3.5-flash", "api_key": None})

    @classmethod
    def get_active_provider(
        cls,
        selected_provider: str = "gemini",
        allowed_providers: list[str] | None = None,
    ) -> AIProvider:
        """Instantiate the requested provider with live model versions & dynamic key resolution."""
        allowed = allowed_providers or ["gemini", "claude", "openai"]
        chosen = selected_provider.lower()

        if chosen not in [p.lower() for p in allowed]:
            logger.warning(f"Provider '{selected_provider}' not in plan allowed list {allowed}. Falling back to 'gemini'.")
            chosen = "gemini"

        config = cls.get_provider_config(chosen)

        try:
            if chosen == "claude":
                api_key = config["api_key"] or getattr(settings, "CLAUDE_API_KEY", "mock_claude_key")
                return ClaudeProvider(api_key=api_key, model_name=config["model_name"])
            elif chosen == "openai":
                api_key = config["api_key"] or getattr(settings, "OPENAI_API_KEY", "mock_openai_key")
                return OpenAIProvider(api_key=api_key, model_name=config["model_name"])
            else:
                api_key = config["api_key"] or settings.GEMINI_API_KEY
                return GeminiProvider(api_key=api_key, model_name=config["model_name"])
        except Exception as e:
            logger.error(f"Failed to instantiate '{chosen}' provider ({e}). Falling back to Gemini 3.5 Flash.")
            return GeminiProvider(api_key=settings.GEMINI_API_KEY, model_name="gemini-3.5-flash")
