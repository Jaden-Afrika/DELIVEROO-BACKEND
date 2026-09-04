from decimal import Decimal, ROUND_HALF_UP
from datetime import datetime, timezone
from typing import Optional

from django.db.models import Q

from app.models.pricing_rule import PricingRule
from app.services.vehicle import get_vehicle_category


def get_pricing_weight_category(weight_kg: float) -> str:
    """Map numeric weight to the legacy pricing-rule tiers.

    Vehicle selection and price tiers are intentionally separate: a bike can
    carry a 4kg parcel, while that parcel still uses the medium price rule.
    """
    weight = float(weight_kg)
    if weight < 0:
        raise ValueError("weight_kg must be greater than or equal to zero")
    if weight <= 2:
        return "light"
    if weight <= 10:
        return "medium"
    return "heavy"


def get_active_pricing_rule(weight_category) -> Optional[PricingRule]:
    if isinstance(weight_category, str):
        weight_category = weight_category
    else:
        weight_category = weight_category.value if hasattr(weight_category, "value") else weight_category
    now = datetime.now(timezone.utc)
    return (
        PricingRule.objects.filter(
            weight_category=weight_category,
            is_active=True,
            effective_from__lte=now,
        )
        .filter(Q(expires_at__isnull=True) | Q(expires_at__gt=now))
        .order_by("-effective_from")
        .first()
    )


def calculate_price(weight_kg: float, distance_km: float) -> dict:
    weight = Decimal(str(weight_kg))
    vehicle_category = get_vehicle_category(weight_kg)
    rule = get_active_pricing_rule(get_pricing_weight_category(weight_kg))
    if rule is None:
        return {
            "base_fee": Decimal("0"),
            "per_km_rate": Decimal("0"),
            "total": Decimal("0"),
            "currency": "KES",
            "rule_found": False,
            "vehicle_category": vehicle_category,
        }
    base = Decimal(str(rule.base_fee))
    per_km = Decimal(str(rule.per_km_rate))
    total = base + (per_km * Decimal(str(distance_km)) * weight)
    return {
        "base_fee": base,
        "per_km_rate": per_km,
        # Frontend estimates use Math.round and KES is displayed as whole
        # shillings, so retain the same half-up rounding on the API quote.
        "total": total.quantize(Decimal("1"), rounding=ROUND_HALF_UP),
        "currency": rule.currency,
        "rule_found": True,
        "vehicle_category": vehicle_category,
    }
