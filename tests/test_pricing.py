from app.services.pricing import calculate_price, get_active_pricing_rule, get_pricing_weight_category
from app.models.enums import WeightCategory
from app.services.vehicle import get_vehicle_category


def test_calculate_price_light(seed_pricing_rules):
    result = calculate_price(2.0, 10.0)
    assert result["rule_found"] is True
    assert result["base_fee"] == 150
    assert result["per_km_rate"] == 15
    assert result["total"] == 450  # 150 + (15 * 10 * 2)
    assert result["currency"] == "KES"


def test_calculate_price_uses_same_rate_for_medium_weight(seed_pricing_rules):
    result = calculate_price(10.0, 20.0)
    assert result["rule_found"] is True
    assert result["total"] == 3150  # 150 + (15 * 20 * 10)


def test_calculate_price_uses_same_rate_for_heavy_weight(seed_pricing_rules):
    result = calculate_price(51.0, 5.0)
    assert result["rule_found"] is True
    assert result["total"] == 3975  # 150 + (15 * 5 * 51)


def test_calculate_price_no_rules(db):
    result = calculate_price(2.0, 10.0)
    assert result["rule_found"] is False
    assert result["total"] == 0


def test_get_active_pricing_rule(seed_pricing_rules):
    rule = get_active_pricing_rule(WeightCategory.light)
    assert rule is not None
    assert rule.base_fee == 150


def test_get_active_pricing_rule_not_found(db):
    rule = get_active_pricing_rule(WeightCategory.heavy)
    assert rule is None


def test_vehicle_category_thresholds():
    assert get_vehicle_category(5.0) == "bike"
    assert get_vehicle_category(5.01) == "car"
    assert get_vehicle_category(50.0) == "car"
    assert get_vehicle_category(50.01) == "lorry"


def test_pricing_tiers_remain_independent_of_vehicle_categories():
    assert get_pricing_weight_category(2.0) == "light"
    assert get_pricing_weight_category(2.01) == "medium"
    assert get_pricing_weight_category(10.0) == "medium"
    assert get_pricing_weight_category(10.01) == "heavy"


def test_bike_parcel_uses_medium_price_when_above_two_kg(seed_pricing_rules):
    result = calculate_price(4.0, 10.0)
    assert result["vehicle_category"] == "bike"
    assert result["total"] == 750  # 150 + (15 * 10 * 4)


def test_price_rounding_matches_frontend_estimate(seed_pricing_rules):
    assert calculate_price(4.0, 5.5)["total"] == 480


def test_price_increases_proportionally_with_weight(seed_pricing_rules):
    one_kg = calculate_price(1.0, 10.0)
    two_kg = calculate_price(2.0, 10.0)

    assert one_kg["total"] == 300
    assert two_kg["total"] == 450


def test_price_does_not_change_rate_at_weight_boundaries(seed_pricing_rules):
    below_boundary = calculate_price(2.0, 10.0)
    above_boundary = calculate_price(2.01, 10.0)

    assert below_boundary["total"] == 450
    assert above_boundary["total"] == 452
