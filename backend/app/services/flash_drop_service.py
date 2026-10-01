import logging
from datetime import datetime, timedelta
from dataclasses import dataclass
from typing import Optional, List, Dict
from uuid import UUID, uuid4

logger = logging.getLogger(__name__)

@dataclass
class FlashDropOffer:
    id: UUID
    appointment_id: UUID
    business_id: UUID
    service_name: str
    staff_name: str
    slot_time: str
    original_price: float
    flash_price: float
    discount_percentage: int
    expires_at: datetime
    is_claimed: bool
    claimed_by_client_id: Optional[UUID]
    broadcast_message: str

class FlashDropService:
    """Last-Minute Flash Drop Engine: Automatically monetizes late cancellations with expiring micro-discounts."""

    FLASH_TEMPLATES = {
        "az": (
            "⚡ *QAYNAR TƏKLİF (FLASH DROP)!*\n\n"
            "Bu gün saat *{slot_time}* üçün {staff_text} '{service_name}' üzrə gözlənilməz boş yer yarandı!\n\n"
            "🏷️ Qiymət: ~{original_price} AZN~ ➔ *{flash_price} AZN* ({discount}% ENDİRİM)\n"
            "⏳ Təklif növbəti *{validity_mins} dəqiqə* ərzində aktivdir.\n\n"
            "Yeri dərhal götürmək üçün birbaşa *BƏLİ* və ya *GÖTÜRÜRƏM* yazın!"
        ),
        "en": (
            "⚡ *LAST-MINUTE FLASH OPENING!*\n\n"
            "A sudden opening just popped up today at *{slot_time}* {staff_text} for '{service_name}'!\n\n"
            "🏷️ Price: ~{original_price} AZN~ ➔ *{flash_price} AZN* ({discount}% OFF)\n"
            "⏳ Valid only for the next *{validity_mins} minutes*.\n\n"
            "Reply *YES* or *CLAIM* to secure this spot instantly!"
        ),
        "ru": (
            "⚡ *ГОРЯЩЕЕ ПРЕДЛОЖЕНИЕ (FLASH DROP)!*\n\n"
            "Сегодня в *{slot_time}* {staff_text} неожиданно освободилось время на '{service_name}'!\n\n"
            "🏷️ Цена: ~{original_price} AZN~ ➔ *{flash_price} AZN* (Скидка {discount}%)\n"
            "⏳ Предложение действует *{validity_mins} минут*.\n\n"
            "Напишите *ДА* или *ЗАБИРАЮ*, чтобы занять место!"
        ),
    }

    def evaluate_cancellation_for_flash_drop(
        self,
        appointment_id: UUID,
        business_id: UUID,
        service_name: str,
        staff_name: str,
        slot_datetime: datetime,
        original_price: float,
        current_time: Optional[datetime] = None,
        discount_percentage: int = 20,
        validity_minutes: int = 25,
        language: str = "az",
        plan_allows_flash_drops: bool = True,
    ) -> Optional[FlashDropOffer]:
        """Evaluates a cancellation and creates an expiring flash offer if slot starts within 1-4 hours."""
        if not plan_allows_flash_drops:
            logger.info(f"[PLAN GATED] Flash drops disabled for plan. Business: {business_id}")
            return None

        now = current_time or datetime.now()
        hours_until_slot = (slot_datetime - now).total_seconds() / 3600.0

        # Trigger only if cancellation happens within 0.5 to 4.5 hours of slot
        if not (0.5 <= hours_until_slot <= 4.5):
            logger.info(f"[FLASH DROP] Slot is {hours_until_slot:.1f} hours away. Outside flash window (0.5-4.5h).")
            return None

        flash_price = round(original_price * (1 - (discount_percentage / 100.0)), 2)
        expires_at = now + timedelta(minutes=validity_minutes)
        slot_time_str = slot_datetime.strftime("%H:%M")

        lang = language if language in self.FLASH_TEMPLATES else "az"
        staff_text_az = f"Usta {staff_name} ilə" if staff_name else ""
        staff_text_en = f"with {staff_name}" if staff_name else ""
        staff_text_ru = f"у мастера {staff_name}" if staff_name else ""
        staff_text = staff_text_az if lang == "az" else (staff_text_en if lang == "en" else staff_text_ru)

        broadcast_msg = self.FLASH_TEMPLATES[lang].format(
            slot_time=slot_time_str,
            staff_text=staff_text,
            service_name=service_name,
            original_price=f"{original_price:.2f}",
            flash_price=f"{flash_price:.2f}",
            discount=discount_percentage,
            validity_mins=validity_minutes,
        )

        offer = FlashDropOffer(
            id=uuid4(),
            appointment_id=appointment_id,
            business_id=business_id,
            service_name=service_name,
            staff_name=staff_name,
            slot_time=slot_time_str,
            original_price=original_price,
            flash_price=flash_price,
            discount_percentage=discount_percentage,
            expires_at=expires_at,
            is_claimed=False,
            claimed_by_client_id=None,
            broadcast_message=broadcast_msg,
        )

        logger.info(f"[FLASH DROP] Generated offer for {service_name} at {slot_time_str} (-{discount_percentage}%)")
        return offer

    def claim_flash_drop(
        self,
        offer: FlashDropOffer,
        client_id: UUID,
        claim_time: Optional[datetime] = None,
    ) -> Dict[str, any]:
        """Atomically claims a flash drop slot for the first replying customer."""
        now = claim_time or datetime.now()

        if offer.is_claimed:
            return {
                "success": False,
                "message": "Təəssüf ki, bu yer artıq başqa müştəri tərəfindən götürüldü.",
                "reason": "already_claimed",
            }

        if now > offer.expires_at:
            return {
                "success": False,
                "message": "Bu qaynar təklifin vaxtı artıq bitmişdir.",
                "reason": "expired",
            }

        offer.is_claimed = True
        offer.claimed_by_client_id = client_id

        logger.info(f"[FLASH DROP] Slot claimed by client {client_id} for {offer.flash_price} AZN!")
        return {
            "success": True,
            "message": f"Təbriklər! Yerinizi təsdiq etdik. Xidmət qiyməti: {offer.flash_price} AZN.",
            "final_price": offer.flash_price,
        }
