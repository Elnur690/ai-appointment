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
    """Detects out-of-scope customer inquiries and triggers automated Human Staff Takeover."""

    OUT_OF_SCOPE_KEYWORDS = {
        "medical": ["allergy", "allergiy", "pain", "ağrı", "doctor", "həkim", "diagnosis", "müalicə", "bleeding", "qanama"],
        "complaint": ["complaint", "şikayət", "bad service", "pis xidmət", "lawyer", "vəkil", "sue", "məhkəmə"],
        "bargaining": ["discount", "güzəşt", "cheaper", "ucuz", "bargain", "hörmət et", "qiyməti düş"],
        "custom_treatment": ["color correction", "rəng korreksiyası", "complex surgery", "əməliyyat"],
    }

    RESPONSE_TEMPLATES = {
        "az": "Bu sual xüsusi diqqət tələb edir. Sizi dərhal əməkdaşımıza yönləndirirəm, az sonra cavablandırılacaq.",
        "en": "This question requires personal assistance. I am transferring you to a team member right away.",
        "ru": "Этот вопрос требует личного внимания. Я привлекаю нашего сотрудника, вам ответят в ближайшее время.",
    }

    def evaluate_message(
        self,
        message_text: str,
        language: str = "az",
        custom_out_of_scope_keywords: list[str] | None = None,
    ) -> GuardrailCheckResult:
        """Evaluates whether an incoming message is out-of-scope and requires human staff intervention."""
        clean_text = message_text.lower().strip()
        lang = language if language in self.RESPONSE_TEMPLATES else "az"

        # Check built-in categories
        for category, keywords in self.OUT_OF_SCOPE_KEYWORDS.items():
            for kw in keywords:
                if kw in clean_text:
                    logger.info(f"[GUARDRAIL TRIGGER] Out-of-scope category '{category}' matched keyword '{kw}'")
                    return GuardrailCheckResult(
                        is_out_of_scope=True,
                        reason=f"Matched out-of-scope keyword '{kw}' in category '{category}'",
                        customer_facing_message=self.RESPONSE_TEMPLATES[lang],
                        should_transfer_to_human=True,
                    )

        # Check custom business rules
        if custom_out_of_scope_keywords:
            for c_kw in custom_out_of_scope_keywords:
                if c_kw.lower().strip() in clean_text:
                    logger.info(f"[GUARDRAIL TRIGGER] Matched custom business out-of-scope rule '{c_kw}'")
                    return GuardrailCheckResult(
                        is_out_of_scope=True,
                        reason=f"Matched custom business out-of-scope rule '{c_kw}'",
                        customer_facing_message=self.RESPONSE_TEMPLATES[lang],
                        should_transfer_to_human=True,
                    )

        return GuardrailCheckResult(
            is_out_of_scope=False,
            reason=None,
            customer_facing_message=None,
            should_transfer_to_human=False,
        )
