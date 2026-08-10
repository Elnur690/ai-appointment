import logging
import httpx
from app.core.config import settings

logger = logging.getLogger(__name__)

class AIModelDiscoveryService:
    """Queries official Google, Anthropic, and OpenAI REST APIs to fetch the latest available models live from source."""

    @staticmethod
    async def discover_gemini_models(api_key: str | None = None) -> list[dict]:
        key = api_key or settings.GEMINI_API_KEY
        url = f"https://generativelanguage.googleapis.com/v1beta/models?key={key}"
        async with httpx.AsyncClient(timeout=10.0) as client:
            try:
                resp = await client.get(url)
                data = resp.json()
                models = data.get("models", [])
                return [
                    {
                        "provider": "gemini",
                        "id": m.get("name", "").replace("models/", ""),
                        "display_name": m.get("displayName", m.get("name")),
                        "description": m.get("description", "")
                    }
                    for m in models if "generateContent" in m.get("supportedGenerationMethods", [])
                ]
            except Exception as e:
                logger.error(f"Failed to discover Gemini models from source: {e}")
                return [{"provider": "gemini", "id": "gemini-3.5-flash", "display_name": "Gemini 3.5 Flash", "description": "Default Fallback"}]

    @staticmethod
    async def discover_claude_models(api_key: str | None = None) -> list[dict]:
        key = api_key or getattr(settings, "CLAUDE_API_KEY", "mock_key")
        url = "https://api.anthropic.com/v1/models"
        headers = {"x-api-key": key, "anthropic-version": "2023-06-01"}
        async with httpx.AsyncClient(timeout=10.0) as client:
            try:
                resp = await client.get(url, headers=headers)
                data = resp.json()
                models = data.get("data", [])
                return [
                    {
                        "provider": "claude",
                        "id": m.get("id"),
                        "display_name": m.get("display_name", m.get("id")),
                        "description": "Anthropic Claude Model"
                    }
                    for m in models
                ]
            except Exception as e:
                logger.error(f"Failed to discover Claude models from source: {e}")
                return [
                    {"provider": "claude", "id": "claude-3-7-sonnet", "display_name": "Claude 3.7 Sonnet", "description": "Latest Sonnet"},
                    {"provider": "claude", "id": "claude-3-5-sonnet-20241022", "display_name": "Claude 3.5 Sonnet", "description": "Sonnet 3.5"},
                ]

    @staticmethod
    async def discover_openai_models(api_key: str | None = None) -> list[dict]:
        key = api_key or getattr(settings, "OPENAI_API_KEY", "mock_key")
        url = "https://api.openai.com/v1/models"
        headers = {"Authorization": f"Bearer {key}"}
        async with httpx.AsyncClient(timeout=10.0) as client:
            try:
                resp = await client.get(url, headers=headers)
                data = resp.json()
                models = data.get("data", [])
                return [
                    {
                        "provider": "openai",
                        "id": m.get("id"),
                        "display_name": m.get("id"),
                        "description": "OpenAI Model"
                    }
                    for m in models if "gpt" in m.get("id", "")
                ]
            except Exception as e:
                logger.error(f"Failed to discover OpenAI models from source: {e}")
                return [{"provider": "openai", "id": "gpt-4o", "display_name": "GPT-4o", "description": "Default GPT-4o"}]

    @classmethod
    async def discover_all_source_models(cls) -> dict[str, list[dict]]:
        """Fetch latest models from Google, Anthropic, and OpenAI concurrently."""
        gemini = await cls.discover_gemini_models()
        claude = await cls.discover_claude_models()
        openai = await cls.discover_openai_models()
        return {
            "gemini": gemini,
            "claude": claude,
            "openai": openai,
        }
