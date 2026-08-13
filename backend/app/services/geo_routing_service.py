import math
import logging
from dataclasses import dataclass
from uuid import UUID

logger = logging.getLogger(__name__)

@dataclass
class BranchDistanceResult:
    branch_id: UUID
    branch_name: str
    address: str
    distance_km: float
    is_nearest: bool

class GeoRoutingService:
    """Calculates GPS Haversine distance & matches Baku landmark keywords to route customers to the nearest branch."""

    LANDMARK_COORDINATES = {
        "28 may": (40.3798, 49.8475),
        "gənclik": (40.4002, 49.8517),
        "genclik": (40.4002, 49.8517),
        "nərimanov": (40.4035, 49.8708),
        "nerimanov": (40.4035, 49.8708),
        "elmlər": (40.3732, 49.8130),
        "elmler": (40.3732, 49.8130),
        "sahil": (40.3698, 49.8415),
    }

    @staticmethod
    def _haversine_km(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
        R = 6371.0  # Earth radius in kilometers
        dlat = math.radians(lat2 - lat1)
        dlon = math.radians(lon2 - lon1)
        a = math.sin(dlat / 2)**2 + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlon / 2)**2
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
        return round(R * c, 2)

    def find_nearest_branch(
        self,
        branches: list[dict],
        lat: float | None = None,
        lng: float | None = None,
        location_text: str | None = None,
    ) -> BranchDistanceResult | None:
        """Finds nearest branch using GPS coordinates or landmark text matching."""
        target_lat, target_lng = lat, lng

        if (target_lat is None or target_lng is None) and location_text:
            text_clean = location_text.strip().lower()
            for landmark, coords in self.LANDMARK_COORDINATES.items():
                if landmark in text_clean:
                    target_lat, target_lng = coords
                    break

        if target_lat is None or target_lng is None or not branches:
            return None

        results = []
        for branch in branches:
            b_lat = branch.get("latitude", 40.3798)
            b_lng = branch.get("longitude", 49.8475)
            dist = self._haversine_km(target_lat, target_lng, b_lat, b_lng)
            results.append(
                BranchDistanceResult(
                    branch_id=branch.get("id"),
                    branch_name=branch.get("name", "Branch"),
                    address=branch.get("address", ""),
                    distance_km=dist,
                    is_nearest=False,
                )
            )

        results.sort(key=lambda r: r.distance_km)
        if results:
            results[0].is_nearest = True
            logger.info(f"[GEO ROUTING] Routed customer location to nearest branch '{results[0].branch_name}' ({results[0].distance_km} km)")
            return results[0]

        return None
