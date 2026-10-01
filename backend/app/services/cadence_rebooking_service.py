import logging
from datetime import datetime, date, timedelta
from dataclasses import dataclass
from typing import List, Optional
from uuid import UUID

logger = logging.getLogger(__name__)

@dataclass
class CadencePredictionResult:
    client_id: UUID
    client_name: str
    service_name: str
    staff_id: Optional[UUID]
    staff_name: Optional[str]
    last_visit_date: date
    cadence_days: int
    predicted_due_date: date
    reminder_date: date
    is_due_for_reminder: bool
    whatsapp_message: Optional[str]

class CadenceRebookingService:
    """Predictive Cadence Rebooking Engine: Computes personalized maintenance intervals and generates automated WhatsApp invitations."""

    DEFAULT_CADENCE_DAYS = {
        "haircut": 18,
        "fade": 16,
        "beard": 14,
        "manicure": 21,
        "pedicure": 28,
        "nails": 24,
        "lashes": 21,
        "hair_color": 42,
        "balayage": 45,
        "facial": 30,
        "botox": 150,
        "dental": 180,
    }

    CADENCE_TEMPLATES = {
        "az": "Salam {name}! Adətən bu vaxtlar {service} xidmətinizi yeniləyirsiniz. {staff_text} {due_day} günü saat {preferred_time} üçün yeriniz hazırdır — təsdiq edək? (Bəli / Xeyr)",
        "en": "Hello {name}! Usually you freshen up your {service} around this time. {staff_text} Your preferred slot on {due_day} at {preferred_time} is open — should we lock it in? (Yes / No)",
        "ru": "Здравствуйте, {name}! Обычно в это время вы обновляете {service}. {staff_text} На {due_day} в {preferred_time} есть свободное время — записать вас? (Да / Нет)",
    }

    def determine_cadence_days(
        self,
        service_key: str,
        visit_history_dates: Optional[List[date]] = None,
    ) -> int:
        """Determines cadence interval based on client historical average or service category preset."""
        if visit_history_dates and len(visit_history_dates) >= 2:
            sorted_dates = sorted(visit_history_dates)
            intervals = [(sorted_dates[i] - sorted_dates[i-1]).days for i in range(1, len(sorted_dates))]
            if intervals:
                avg_interval = sum(intervals) // len(intervals)
                if 7 <= avg_interval <= 365:
                    return avg_interval

        clean_key = service_key.lower().strip()
        for k, v in self.DEFAULT_CADENCE_DAYS.items():
            if k in clean_key:
                return v
        return 21  # default 3 weeks

    def evaluate_client_cadence(
        self,
        client_id: UUID,
        client_name: str,
        service_name: str,
        last_visit_date: date,
        current_date: Optional[date] = None,
        staff_id: Optional[UUID] = None,
        staff_name: Optional[str] = None,
        preferred_time: str = "18:00",
        language: str = "az",
        visit_history_dates: Optional[List[date]] = None,
        plan_allows_cadence_engine: bool = True,
    ) -> Optional[CadencePredictionResult]:
        """Calculates client due date and generates invitation message if due within reminder window."""
        if not plan_allows_cadence_engine:
            logger.info(f"[PLAN GATED] Cadence engine disabled for plan. Skipping client {client_id}")
            return None

        today = current_date or date.today()
        cadence_days = self.determine_cadence_days(service_name, visit_history_dates)
        predicted_due = last_visit_date + timedelta(days=cadence_days)
        reminder_date = predicted_due - timedelta(days=3)  # Send reminder 3 days in advance

        is_due = today >= reminder_date

        whatsapp_msg = None
        if is_due:
            lang = language if language in self.CADENCE_TEMPLATES else "az"
            staff_text_az = f"Usta {staff_name} ilə" if staff_name else ""
            staff_text_en = f"With {staff_name}" if staff_name else ""
            staff_text_ru = f"У мастера {staff_name}" if staff_name else ""

            staff_text = staff_text_az if lang == "az" else (staff_text_en if lang == "en" else staff_text_ru)
            due_day_str = predicted_due.strftime("%A, %d %B")

            template = self.CADENCE_TEMPLATES[lang]
            whatsapp_msg = template.format(
                name=client_name,
                service=service_name,
                staff_text=staff_text,
                due_day=due_day_str,
                preferred_time=preferred_time,
            ).strip()

        return CadencePredictionResult(
            client_id=client_id,
            client_name=client_name,
            service_name=service_name,
            staff_id=staff_id,
            staff_name=staff_name,
            last_visit_date=last_visit_date,
            cadence_days=cadence_days,
            predicted_due_date=predicted_due,
            reminder_date=reminder_date,
            is_due_for_reminder=is_due,
            whatsapp_message=whatsapp_msg,
        )
