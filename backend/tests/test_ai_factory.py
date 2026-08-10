import pytest
from app.integrations.ai.factory import AIProviderFactory
from app.integrations.ai.gemini_provider import GeminiProvider
from app.integrations.ai.claude_provider import ClaudeProvider
from app.integrations.ai.openai_provider import OpenAIProvider

def test_ai_factory_gemini_selection():
    provider = AIProviderFactory.get_provider(
        selected_provider="gemini",
        allowed_providers=["gemini", "claude"],
        gemini_api_key="mock_key"
    )
    assert isinstance(provider, GeminiProvider)

def test_ai_factory_claude_selection():
    provider = AIProviderFactory.get_provider(
        selected_provider="claude",
        allowed_providers=["gemini", "claude"],
        claude_api_key="mock_key"
    )
    assert isinstance(provider, ClaudeProvider)

def test_ai_factory_openai_selection():
    provider = AIProviderFactory.get_provider(
        selected_provider="openai",
        allowed_providers=["gemini", "openai"],
        openai_api_key="mock_key"
    )
    assert isinstance(provider, OpenAIProvider)

def test_ai_factory_plan_fallback():
    # If business chooses 'claude' but plan only allows ['gemini'], fallback to Gemini
    provider = AIProviderFactory.get_provider(
        selected_provider="claude",
        allowed_providers=["gemini"],
        gemini_api_key="mock_key"
    )
    assert isinstance(provider, GeminiProvider)
