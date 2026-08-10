import pytest
from decimal import Decimal
from uuid import uuid4
from datetime import date

from app.services.no_show_protection_service import NoShowProtectionService
from app.services.emergency_reassignment_service import EmergencyReassignmentService
from app.integrations.omnichannel.channel_handler import OmnichannelHandler
from app.services.business_advisor_service import BusinessAdvisorService
from app.services.custom_domain_service import CustomDomainService

def test_feature_1_no_show_protection():
    service = NoShowProtectionService()
    # Test 2+ no-shows requires deposit
    req = service.evaluate_booking_risk(customer_no_shows=2, service_price=Decimal("30.00"))
    assert req.is_deposit_required is True
    assert req.deposit_amount == Decimal("10.00")
    assert req.checkout_url is not None

@pytest.mark.asyncio
async def test_feature_2_emergency_staff_replacement():
    service = EmergencyReassignmentService()
    sick_staff = uuid4()
    replacement_staff = uuid4()
    outcomes = await service.handle_staff_emergency_leave(
        branch_id=uuid4(),
        sick_staff_id=sick_staff,
        leave_date=date.today(),
        available_staff_ids=[replacement_staff],
    )
    assert len(outcomes) == 2
    assert outcomes[0].assigned_staff_id == replacement_staff
    assert outcomes[0].status == "reassigned"

def test_feature_3_omnichannel_ig_fb_handler():
    handler = OmnichannelHandler()
    meta_payload = {
        "entry": [
            {
                "messaging": [
                    {
                        "sender": {"id": "ig_user_123"},
                        "recipient": {"id": "page_456"},
                        "message": {"mid": "msg_99", "text": "Do you have time tomorrow at 2 PM?"},
                        "timestamp": 1700000000,
                    }
                ]
            }
        ]
    }
    parsed = handler.parse_meta_webhook(meta_payload, channel="instagram")
    assert parsed is not None
    assert parsed.sender_phone == "ig_user_123"
    assert parsed.message_text == "Do you have time tomorrow at 2 PM?"

def test_feature_4_business_growth_advisor():
    advisor = BusinessAdvisorService()
    report = advisor.generate_weekly_report(business_id="b1", business_name="Beauty Studio Baku")
    assert report.business_id == "b1"
    assert "Saturday" in report.peak_demand_slot
    assert report.estimated_lost_revenue_cancellations == Decimal("180.00")

@pytest.mark.asyncio
async def test_feature_5_custom_domain_cname():
    service = CustomDomainService()
    biz_id = uuid4()
    status = await service.verify_and_provision_cname("booking.mysalon.az", biz_id)
    assert status.custom_domain == "booking.mysalon.az"
    assert status.is_cname_valid is True
    assert status.is_ssl_active is True
