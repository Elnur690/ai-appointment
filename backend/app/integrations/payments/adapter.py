from abc import ABC, abstractmethod
from dataclasses import dataclass
from decimal import Decimal
from typing import Any, Dict
from uuid import UUID

@dataclass
class PaymentLinkResult:
    payment_url: str
    transaction_id: str

@dataclass
class WebhookResult:
    transaction_id: str
    is_successful: bool
    amount: Decimal
    raw_data: Dict[str, Any]

class PaymentStatus(ABC):
    pass

class PaymentAdapter(ABC):
    @abstractmethod
    async def create_payment_link(
        self,
        payment_id: UUID,
        amount: Decimal,
        currency: str,
        description: str,
        merchant_config: Dict[str, Any],
        return_url: str
    ) -> PaymentLinkResult:
        """Create a payment link for the checkout session."""
        pass

    @abstractmethod
    async def verify_webhook(
        self,
        payload: Dict[str, Any],
        headers: Dict[str, str],
        merchant_config: Dict[str, Any]
    ) -> WebhookResult:
        """Verify incoming webhook from the payment gateway."""
        pass

    @abstractmethod
    async def check_status(
        self,
        transaction_id: str,
        merchant_config: Dict[str, Any]
    ) -> str:
        """Check the status of a payment transaction."""
        pass
