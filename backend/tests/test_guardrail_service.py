import pytest
from app.services.guardrail_service import GuardrailService

def test_guardrail_solo_business_az():
    service = GuardrailService()
    result = service.evaluate_message("Mənim xidmətdən şikayətim var!", language="az", is_solo_business=True)
    assert result.is_out_of_scope is True
    assert result.should_transfer_to_human is True
    # Verify 1st-person singular solo wording ("özümlə dəqiqləşdirib az sonra sizə şəxsən yazacağam")
    assert "şəxsən yazacağam" in result.customer_facing_message

def test_guardrail_multi_staff_business_en():
    service = GuardrailService()
    result = service.evaluate_message("I am experiencing severe skin allergy pain after the treatment", language="en", is_solo_business=False)
    assert result.is_out_of_scope is True
    assert result.should_transfer_to_human is True
    # Verify natural team wording ("with our team")
    assert "with our team" in result.customer_facing_message

def test_guardrail_normal_booking_question():
    service = GuardrailService()
    result = service.evaluate_message("Sabah saat 14:00-da saç kəsimi üçün yer var?", language="az")
    assert result.is_out_of_scope is False
    assert result.should_transfer_to_human is False
