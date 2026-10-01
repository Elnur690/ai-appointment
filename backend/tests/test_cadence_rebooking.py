try:
    import pytest
except ImportError:
    pass
from datetime import date, timedelta
from uuid import uuid4
from app.services.cadence_rebooking_service import CadenceRebookingService

def test_determine_cadence_days_default():
    service = CadenceRebookingService()
    days = service.determine_cadence_days("Men's Fade & Beard Trim")
    assert days == 16

    days_nails = service.determine_cadence_days("Gel Nails Refill")
    assert days_nails == 24

def test_determine_cadence_days_custom_history():
    service = CadenceRebookingService()
    history = [
        date(2026, 1, 1),
        date(2026, 1, 15), # 14 days
        date(2026, 1, 30), # 15 days
    ]
    avg_days = service.determine_cadence_days("Haircut", history)
    assert avg_days == 14

def test_evaluate_client_cadence_due():
    service = CadenceRebookingService()
    client_id = uuid4()
    last_visit = date(2026, 9, 10)
    current_date = date(2026, 9, 25) # 15 days later (cadence is 16 days, reminder 3 days prior: 13 days)

    result = service.evaluate_client_cadence(
        client_id=client_id,
        client_name="Murad",
        service_name="Men's Fade",
        last_visit_date=last_visit,
        current_date=current_date,
        staff_name="Elvin",
        language="az",
        plan_allows_cadence_engine=True,
    )

    assert result is not None
    assert result.is_due_for_reminder is True
    assert "Murad" in result.whatsapp_message
    assert "Usta Elvin" in result.whatsapp_message
    assert "təsdiq edək?" in result.whatsapp_message

def test_evaluate_client_cadence_plan_gated():
    service = CadenceRebookingService()
    result = service.evaluate_client_cadence(
        client_id=uuid4(),
        client_name="Leyla",
        service_name="Haircut",
        last_visit_date=date(2026, 9, 1),
        current_date=date(2026, 9, 25),
        plan_allows_cadence_engine=False,
    )
    assert result is None
