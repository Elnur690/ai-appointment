import pytest
from app.services.guardrail_service import GuardrailService

def test_guardrail_detects_complaint_az():
    service = GuardrailService()
    result = service.evaluate_message("Mənim xidmətdən şikayətim var!", language="az")
    assert result.is_out_of_scope is True
    assert result.should_transfer_to_human is True
    assert "əməkdaşımıza yönləndirirəm" in result.customer_facing_message

def test_guardrail_detects_medical_en():
    service = GuardrailService()
    result = service.evaluate_message("I am experiencing severe skin allergy pain after the treatment", language="en")
    assert result.is_out_of_scope is True
    assert result.should_transfer_to_human is True
    assert "transferring you to a team member" in result.customer_facing_message

def test_guardrail_normal_booking_question():
    service = GuardrailService()
    result = service.evaluate_message("Sabah saat 14:00-da saç kəsimi üçün yer var?", language="az")
    assert result.is_out_of_scope is False
    assert result.should_transfer_to_human is False

def test_guardrail_custom_business_rule():
    service = GuardrailService()
    result = service.evaluate_message("Qiyməti 50 AZN-dən 30 AZN-ə düşə bilərsiniz?", language="az", custom_out_of_scope_keywords=["qiyməti düş"])
    assert result.is_out_of_scope is True
    assert result.should_transfer_to_human is True
