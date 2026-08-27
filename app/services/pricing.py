from decimal import Decimal
from datetime import datetime, timezone
from typing import Optional

from django.db.models import Q

from app.models.pricing_rule import PricingRule


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


def calculate_price(weight_category, distance_km: float) -> dict:
    rule = get_active_pricing_rule(weight_category)
    if rule is None:
        return {
            "base_fee": Decimal("0"),
            "per_km_rate": Decimal("0"),
            "total": Decimal("0"),
            "currency": "KES",
            "rule_found": False,
        }
    base = Decimal(str(rule.base_fee))
    per_km = Decimal(str(rule.per_km_rate))
    total = base + (per_km * Decimal(str(distance_km)))
    return {
        "base_fee": base,
        "per_km_rate": per_km,
        "total": total.quantize(Decimal("0.01")),
        "currency": rule.currency,
        "rule_found": True,
    }
