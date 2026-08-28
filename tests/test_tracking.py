def _create_parcel(client, auth_header, **overrides):
    payload = {
        "pickupLocation": "Westlands, Nairobi",
        "destination": "Kilimani, Nairobi",
        "weightCategory": "medium",
        "distanceKm": 10.0,
    }
    payload.update(overrides)
    resp = client.post("/parcels", payload, **auth_header, format="json")
    return resp.json() if resp.status_code == 201 else None


class TestTracking:
    def test_tracking_returns_200_not_501(self, client, auth_header, seed_pricing_rules, seed_users):
        parcel = _create_parcel(client, auth_header)
        resp = client.get(f"/parcels/{parcel['id']}/tracking", **auth_header)
        assert resp.status_code == 200

    def test_tracking_contains_pickup_and_destination_coordinates(
        self, client, auth_header, seed_pricing_rules, seed_users
    ):
        parcel = _create_parcel(client, auth_header)
        resp = client.get(f"/parcels/{parcel['id']}/tracking", **auth_header)
        data = resp.json()
        assert data["pickup"]["label"] == "Westlands, Nairobi"
        assert data["pickup"]["latitude"] is not None
        assert data["pickup"]["longitude"] is not None
        assert data["destination"]["label"] == "Kilimani, Nairobi"
        assert data["destination"]["latitude"] is not None
        assert data["destination"]["longitude"] is not None

    def test_tracking_contains_status_and_distance(self, client, auth_header, seed_pricing_rules, seed_users):
        parcel = _create_parcel(client, auth_header)
        resp = client.get(f"/parcels/{parcel['id']}/tracking", **auth_header)
        data = resp.json()
        assert data["status"] == "pending"
        assert data["distanceKm"] == 10.0
        assert data["estimatedTravelTime"] is not None

    def test_tracking_reflects_latest_status_history_note(
        self, client, admin_header, auth_header, seed_pricing_rules, seed_users
    ):
        parcel = _create_parcel(client, auth_header)
        client.patch(
            f"/admin/parcels/{parcel['id']}/status",
            {"status": "in_transit"},
            **admin_header, format="json",
        )
        resp = client.get(f"/parcels/{parcel['id']}/tracking", **auth_header)
        data = resp.json()
        assert data["status"] == "in_transit"
        assert "in_transit" in data["lastUpdateNote"]

    def test_non_owner_cannot_track(self, client, auth_header, other_header, seed_pricing_rules, seed_users):
        parcel = _create_parcel(client, auth_header)
        resp = client.get(f"/parcels/{parcel['id']}/tracking", **other_header)
        assert resp.status_code == 404

    def test_unauthenticated_cannot_track(self, client, auth_header, seed_pricing_rules, seed_users):
        parcel = _create_parcel(client, auth_header)
        resp = client.get(f"/parcels/{parcel['id']}/tracking")
        assert resp.status_code == 401

    def test_admin_can_track_any_parcel(self, client, auth_header, admin_header, seed_pricing_rules, seed_users):
        parcel = _create_parcel(client, auth_header)
        resp = client.get(f"/parcels/{parcel['id']}/tracking", **admin_header)
        assert resp.status_code == 200
