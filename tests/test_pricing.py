import pytest
from app.services.pricing import calculate_price, get_active_pricing_rule
from app.models.enums import WeightCategory


def test_calculate_price_light(seed_pricing_rules):
    result = calculate_price(WeightCategory.light, 10.0)
    assert result["rule_found"] is True
    assert result["base_fee"] == 150
    assert result["per_km_rate"] == 15
    assert result["total"] == 300  # 150 + (15 * 10)
    assert result["currency"] == "KES"


def test_calculate_price_medium(seed_pricing_rules):
    result = calculate_price(WeightCategory.medium, 20.0)
    assert result["rule_found"] is True
    assert result["total"] == 850  # 350 + (25 * 20)


def test_calculate_price_heavy(seed_pricing_rules):
    result = calculate_price(WeightCategory.heavy, 5.0)
    assert result["rule_found"] is True
    assert result["total"] == 900  # 700 + (40 * 5)


def test_calculate_price_no_rules(db_session):
    result = calculate_price(WeightCategory.light, 10.0)
    assert result["rule_found"] is False
    assert result["total"] == 0


def test_get_active_pricing_rule(seed_pricing_rules):
    rule = get_active_pricing_rule(WeightCategory.light)
    assert rule is not None
    assert rule.base_fee == 150


def test_get_active_pricing_rule_not_found(db_session):
    rule = get_active_pricing_rule(WeightCategory.heavy)
    assert rule is None
