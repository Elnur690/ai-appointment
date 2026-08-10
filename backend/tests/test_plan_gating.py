import pytest
from uuid import uuid4
from app.models.saas import Plan

def test_plan_feature_flags_defaults():
    plan = Plan(
        id=uuid4(),
        name="Basic Plan",
        price=29.00,
        max_branches=1,
        max_whatsapp_numbers=1,
        ai_message_quota=500,
    )
    assert plan.allows_branch_level_ai_tone is False
    assert plan.allows_voice_messages is False
    assert plan.allows_dynamic_pricing is False
    assert plan.allows_winback_campaigns is False

def test_pro_plan_feature_flags_enabled():
    plan = Plan(
        id=uuid4(),
        name="Enterprise Pro Plan",
        price=149.00,
        max_branches=10,
        max_whatsapp_numbers=5,
        ai_message_quota=5000,
        allows_branch_level_ai_tone=True,
        allows_voice_messages=True,
        allows_dynamic_pricing=True,
        allows_winback_campaigns=True,
    )
    assert plan.allows_voice_messages is True
    assert plan.allows_dynamic_pricing is True
    assert plan.allows_winback_campaigns is True
