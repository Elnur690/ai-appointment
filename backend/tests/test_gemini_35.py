import pytest
from app.core.config import settings
from app.integrations.ai.gemini_provider import GeminiProvider

def test_gemini_35_default_config():
    assert settings.GEMINI_MODEL == "gemini-3.5-flash"

def test_gemini_provider_default_model():
    provider = GeminiProvider(api_key="mock_key")
    assert provider.model_name == "gemini-3.5-flash"
