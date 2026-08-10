import pytest
from app.services.ai_model_discovery_service import AIModelDiscoveryService

@pytest.mark.asyncio
async def test_ai_model_discovery_all_sources():
    models = await AIModelDiscoveryService.discover_all_source_models()
    assert "gemini" in models
    assert "claude" in models
    assert "openai" in models
    assert len(models["gemini"]) > 0
    assert len(models["claude"]) > 0
    assert len(models["openai"]) > 0
