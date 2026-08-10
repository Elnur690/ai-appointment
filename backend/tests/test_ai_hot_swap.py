import pytest
from app.services.ai_registry import AIRegistryService
from app.integrations.ai.factory import AIProviderFactory
from app.integrations.ai.claude_provider import ClaudeProvider

def test_hot_swap_model_version():
    # Update Claude model version live to 'claude-3-7-sonnet'
    AIRegistryService.update_provider_config("claude", model_name="claude-3-7-sonnet", api_key="new_live_key")
    
    provider = AIProviderFactory.get_provider(
        selected_provider="claude",
        allowed_providers=["gemini", "claude"]
    )
    assert isinstance(provider, ClaudeProvider)
    assert provider.model_name == "claude-3-7-sonnet"
    assert provider.api_key == "new_live_key"

def test_hot_swap_api_key_rotation():
    AIRegistryService.update_provider_config("claude", api_key="rotated_key_999")
    config = AIRegistryService.get_provider_config("claude")
    assert config["api_key"] == "rotated_key_999"
