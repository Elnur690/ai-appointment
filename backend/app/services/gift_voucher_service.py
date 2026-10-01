import logging
import random
import string
from datetime import datetime, date, timedelta
from dataclasses import dataclass
from typing import Optional, Dict
from uuid import UUID, uuid4

logger = logging.getLogger(__name__)

@dataclass
class GiftVoucher:
    id: UUID
    code: str
    business_id: UUID
    amount_azn: float
    service_name: Optional[str]
    sender_name: str
    recipient_name: str
    recipient_phone: str
    greeting_message: str
    expires_at: date
    is_paid: bool
    is_redeemed: bool
    payment_url: Optional[str]
    delivery_message: Optional[str]

class GiftVoucherService:
    """WhatsApp Digital Gift Vouchers & Celebration Gifting Engine."""

    VOUCHER_TEMPLATES = {
        "az": (
            "🎉 Təbriklər {recipient_name}! {sender_name} sizə '{business_name}' üçün "
            "{value_text} Hədiyyə Sertifikatı göndərdi!\n\n"
            "💌 Təbrik mesajı: \"{greeting}\"\n"
            "🎟️ VAUÇER KODU: *{code}*\n"
            "⏳ Bitmə tarixi: {expires_date}\n\n"
            "Bronlaşdırmaq üçün birbaşa bu nömrəyə yaza bilərsiniz!"
        ),
        "en": (
            "🎉 Congratulations {recipient_name}! {sender_name} has gifted you a "
            "{value_text} Gift Voucher for '{business_name}'!\n\n"
            "💌 Personal Note: \"{greeting}\"\n"
            "🎟️ VOUCHER CODE: *{code}*\n"
            "⏳ Valid until: {expires_date}\n\n"
            "To book your appointment, simply message this WhatsApp number!"
        ),
        "ru": (
            "🎉 Поздравляем, {recipient_name}! {sender_name} подарил(а) вам "
            "Подарочный Сертификат на {value_text} в '{business_name}'!\n\n"
            "💌 Пожелание: \"{greeting}\"\n"
            "🎟️ КОД ВАУЧЕРА: *{code}*\n"
            "⏳ Действителен до: {expires_date}\n\n"
            "Для записи просто напишите на этот номер WhatsApp!"
        ),
    }

    def _generate_code(self) -> str:
        chars = string.ascii_uppercase + string.digits
        random_suffix = ''.join(random.choices(chars, k=6))
        return f"GIFT-{random_suffix}"

    def create_gift_voucher(
        self,
        business_id: UUID,
        business_name: str,
        sender_name: str,
        recipient_name: str,
        recipient_phone: str,
        amount_azn: float,
        service_name: Optional[str] = None,
        greeting_message: str = "Təbriklər!",
        validity_days: int = 180,
        language: str = "az",
        plan_allows_gift_vouchers: bool = True,
    ) -> Optional[GiftVoucher]:
        """Creates a pending digital gift voucher with automated celebration message."""
        if not plan_allows_gift_vouchers:
            logger.warning(f"[PLAN GATED] Gift vouchers not allowed on plan for business {business_id}")
            return None

        voucher_code = self._generate_code()
        expires_at = date.today() + timedelta(days=validity_days)
        voucher_id = uuid4()

        # Generate Payriff checkout URL for upfront voucher payment
        payment_url = f"https://checkout.payriff.com/v1/gift/{voucher_id}"

        value_text = f"{amount_azn:.2f} AZN" if not service_name else f"'{service_name}' ({amount_azn:.2f} AZN)"
        lang = language if language in self.VOUCHER_TEMPLATES else "az"
        template = self.VOUCHER_TEMPLATES[lang]

        delivery_msg = template.format(
            recipient_name=recipient_name,
            sender_name=sender_name,
            business_name=business_name,
            value_text=value_text,
            greeting=greeting_message,
            code=voucher_code,
            expires_date=expires_at.strftime("%d.%m.%Y"),
        )

        voucher = GiftVoucher(
            id=voucher_id,
            code=voucher_code,
            business_id=business_id,
            amount_azn=amount_azn,
            service_name=service_name,
            sender_name=sender_name,
            recipient_name=recipient_name,
            recipient_phone=recipient_phone,
            greeting_message=greeting_message,
            expires_at=expires_at,
            is_paid=False,
            is_redeemed=False,
            payment_url=payment_url,
            delivery_message=delivery_msg,
        )

        logger.info(f"[GIFT VOUCHER] Created voucher {voucher_code} for {recipient_name} ({amount_azn} AZN)")
        return voucher

    def redeem_voucher(
        self,
        voucher: GiftVoucher,
        appointment_total_azn: float,
        current_date: Optional[date] = None,
    ) -> Dict[str, any]:
        """Validates voucher eligibility, checks expiry, and calculates discount."""
        today = current_date or date.today()

        if not voucher.is_paid:
            return {"success": False, "discount_azn": 0.0, "reason": "Voucher has not been paid yet."}

        if voucher.is_redeemed:
            return {"success": False, "discount_azn": 0.0, "reason": "Voucher has already been redeemed."}

        if today > voucher.expires_at:
            return {"success": False, "discount_azn": 0.0, "reason": "Voucher has expired."}

        discount = min(voucher.amount_azn, appointment_total_azn)
        remaining_balance = max(0.0, appointment_total_azn - discount)

        return {
            "success": True,
            "voucher_code": voucher.code,
            "discount_azn": discount,
            "final_payable_azn": remaining_balance,
            "reason": "Voucher successfully applied.",
        }
