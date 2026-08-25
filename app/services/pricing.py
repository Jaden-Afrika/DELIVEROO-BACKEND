from decimal import Decimal
from datetime import datetime, timezone
from typing import Optional

from app.extensions import db
from app.models.enums import WeightCategory
from app.models.pricing_rule import PricingRule


def get_active_pricing_rule(
    weight_category: WeightCategory, session=None
) -> Optional[PricingRule]:
    session = session or db.session
    now = datetime.now(timezone.utc)
    return (
        session.query(PricingRule)
        .filter(
            PricingRule.weight_category == weight_category,
            PricingRule.is_active == True,  # noqa: E712
            PricingRule.effective_from <= now,
            db.or_(PricingRule.expires_at == None, PricingRule.expires_at > now),  # noqa: E712
        )
        .order_by(PricingRule.effective_from.desc())
        .first()
    )


def calculate_price(weight_category: WeightCategory, distance_km: float) -> dict:
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
