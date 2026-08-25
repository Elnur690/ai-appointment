import logging
from dataclasses import dataclass

logger = logging.getLogger(__name__)

@dataclass
class GuardrailCheckResult:
    is_out_of_scope: bool
    reason: str | None
    customer_facing_message: str | None
    should_transfer_to_human: bool

class GuardrailService:
    """Detects out-of-scope customer inquiries and triggers automated Human Staff Takeover with human-like tone."""

    OUT_OF_SCOPE_KEYWORDS = {
        "medical": ["allergy", "allergiy", "pain", "ağrı", "doctor", "həkim", "diagnosis", "müalicə", "bleeding", "qanama"],
        "complaint": ["complaint", "şikayət", "bad service", "pis xidmət", "lawyer", "vəkil", "sue", "məhkəmə"],
        "bargaining": ["discount", "güzəşt", "cheaper", "ucuz", "bargain", "hörmət et", "qiyməti düş"],
        "custom_treatment": ["color correction", "rəng korreksiyası", "complex surgery", "əməliyyat"],
    }

    # Human-like 1st person singular for Solo Operated Businesses (Barbers, Estheticians, Solo Doctors)
    SOLO_RESPONSE_TEMPLATES = {
        "az": "Bu barədə özümlə dəqiqləşdirib az sonra sizə şəxsən yazacağam.",
        "en": "Let me double-check this for you personally and I'll get back to you in just a moment.",
        "ru": "Я лично уточню этот вопрос и отвечу вам в ближайшее время.",
    }

    # Natural team templates for Multi-Staff Salons/Clinics
    TEAM_RESPONSE_TEMPLATES = {
        "az": "Bu məsələni komandamızla dəqiqləşdirib az sonra sizə mütləq məlumat verəcəyik.",
        "en": "Let me check on this with our team and we'll update you in just a moment.",
        "ru": "Мы уточним этот вопрос с командой и обязательно свяжемся с вами.",
    }

    def evaluate_message(
        self,
        message_text: str,
        language: str = "az",
        is_solo_business: bool = False,
        custom_out_of_scope_keywords: list[str] | None = None,
    ) -> GuardrailCheckResult:
        """Evaluates whether an incoming message is out-of-scope and selects a 100% natural, human-like response."""
        clean_text = message_text.lower().strip()
        lang = language if language in self.SOLO_RESPONSE_TEMPLATES else "az"

        templates = self.SOLO_RESPONSE_TEMPLATES if is_solo_business else self.TEAM_RESPONSE_TEMPLATES
        reply_text = templates[lang]

        # Check built-in categories
        for category, keywords in self.OUT_OF_SCOPE_KEYWORDS.items():
            for kw in keywords:
                if kw in clean_text:
                    logger.info(f"[GUARDRAIL TRIGGER] Out-of-scope category '{category}' matched keyword '{kw}' (Solo={is_solo_business})")
                    return GuardrailCheckResult(
                        is_out_of_scope=True,
                        reason=f"Matched out-of-scope keyword '{kw}' in category '{category}'",
                        customer_facing_message=reply_text,
                        should_transfer_to_human=True,
                    )

        # Check custom business rules
        if custom_out_of_scope_keywords:
            for c_kw in custom_out_of_scope_keywords:
                if c_kw.lower().strip() in clean_text:
                    logger.info(f"[GUARDRAIL TRIGGER] Matched custom business out-of-scope rule '{c_kw}' (Solo={is_solo_business})")
                    return GuardrailCheckResult(
                        is_out_of_scope=True,
                        reason=f"Matched custom business out-of-scope rule '{c_kw}'",
                        customer_facing_message=reply_text,
                        should_transfer_to_human=True,
                    )

        return GuardrailCheckResult(
            is_out_of_scope=False,
            reason=None,
            customer_facing_message=None,
            should_transfer_to_human=False,
        )
