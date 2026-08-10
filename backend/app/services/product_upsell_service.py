import logging
from dataclasses import dataclass
from decimal import Decimal

logger = logging.getLogger(__name__)

@dataclass
class ProductUpsellRecommendation:
    product_name: str
    price: Decimal
    description: str
    pickup_at_appointment: bool

class ProductUpsellService:
    """Generates physical retail product add-on recommendations post-appointment confirmation."""

    UPSELL_CATALOG = {
        "haircut": ProductUpsellRecommendation(
            product_name="Organic Argan Hair & Scalp Oil",
            price=Decimal("25.00"),
            description="Nourishing organic hair oil for daily styling.",
            pickup_at_appointment=True,
        ),
        "beard": ProductUpsellRecommendation(
            product_name="Beard Balm & Care Wax",
            price=Decimal("15.00"),
            description="Premium sandalwood beard care wax.",
            pickup_at_appointment=True,
        ),
    }

    def get_upsell_recommendation(self, service_category: str, allows_upsell: bool = True) -> ProductUpsellRecommendation | None:
        if not allows_upsell:
            return None
        return self.UPSELL_CATALOG.get(service_category.lower())
