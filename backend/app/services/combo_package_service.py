import logging
from dataclasses import dataclass
from decimal import Decimal

logger = logging.getLogger(__name__)

@dataclass
class ComboPackageResult:
    package_name: str
    total_duration_minutes: int
    original_total_price: Decimal
    combo_discounted_price: Decimal
    discount_savings: Decimal

class ComboPackageService:
    """Calculates multi-service combo package time blocks and pricing discounts."""

    def calculate_combo_package(self, services: list[dict], allows_combo: bool = True) -> ComboPackageResult:
        total_duration = sum(s.get("duration", 30) for s in services)
        base_price = sum(Decimal(str(s.get("price", 0))) for s in services)

        if not allows_combo or len(services) < 2:
            return ComboPackageResult(
                package_name="Individual Services",
                total_duration_minutes=total_duration,
                original_total_price=base_price,
                combo_discounted_price=base_price,
                discount_savings=Decimal("0.00"),
            )

        # 15% combo package discount for multi-service bookings
        combo_price = Decimal(str(round(float(base_price) * 0.85, 2)))
        savings = base_price - combo_price
        package_name = " + ".join(s.get("name", "Service") for s in services) + " Combo"

        return ComboPackageResult(
            package_name=package_name,
            total_duration_minutes=total_duration,
            original_total_price=base_price,
            combo_discounted_price=combo_price,
            discount_savings=savings,
        )
