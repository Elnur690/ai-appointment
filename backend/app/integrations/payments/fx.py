import logging
import time
from decimal import Decimal, ROUND_HALF_UP
import httpx

logger = logging.getLogger(__name__)

_FX_CACHE: dict[str, float | Decimal] = {
    "rate": Decimal("0.588235"),  # 1 / 1.70 fallback
    "fetched_at": 0.0,
}
_CACHE_TTL_SECONDS = 3600


async def get_azn_to_usd_rate() -> Decimal:
    """Fetch live AZN -> USD exchange rate with 1-hour in-memory cache."""
    now = time.time()
    if now - float(_FX_CACHE["fetched_at"]) < _CACHE_TTL_SECONDS:
        return Decimal(str(_FX_CACHE["rate"]))

    try:
        async with httpx.AsyncClient(timeout=8.0) as client:
            resp = await client.get("https://open.er-api.com/v6/latest/AZN")
            if resp.status_code == 200:
                data = resp.json()
                usd_rate = data.get("rates", {}).get("USD")
                if usd_rate and float(usd_rate) > 0:
                    rate_dec = Decimal(str(usd_rate))
                    _FX_CACHE["rate"] = rate_dec
                    _FX_CACHE["fetched_at"] = now
                    return rate_dec
    except Exception as exc:
        logger.warning(f"Live FX rate lookup failed, using cached/fallback AZN->USD rate: {exc}")

    return Decimal(str(_FX_CACHE["rate"]))


async def convert_to_usd(amount: Decimal, currency: str) -> tuple[Decimal, Decimal]:
    """Convert AZN (or USD) amount to USD using live FX rate. Returns (usd_amount, rate_used)."""
    curr = (currency or "AZN").strip().upper()
    if curr == "USD":
        return Decimal(str(amount)).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP), Decimal("1.000000")

    rate = await get_azn_to_usd_rate()
    usd_val = (Decimal(str(amount)) * rate).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
    return usd_val, rate.quantize(Decimal("0.000001"), rounding=ROUND_HALF_UP)
