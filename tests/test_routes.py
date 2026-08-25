def test_route_registration(app):
    rules = {rule.rule for rule in app.url_map.iter_rules()}
    assert "/auth/signup" in rules
    assert "/auth/login" in rules
    assert "/auth/logout" in rules
    assert "/auth/me" in rules
    assert "/parcels/me" in rules
    assert "/parcels" in rules
    assert "/parcels/<int:parcel_id>" in rules
    assert "/parcels/<int:parcel_id>/cancel" in rules
    assert "/parcels/<int:parcel_id>/destination" in rules
    assert "/parcels/<int:parcel_id>/status-history" in rules
    assert "/parcels/<int:parcel_id>/tracking" in rules
    assert "/admin/parcels" in rules
    assert "/admin/parcels/<int:parcel_id>/status" in rules
    assert "/admin/parcels/<int:parcel_id>/location" in rules
    assert "/" in rules
    assert "/health" in rules
    assert "/openapi.json" in rules
