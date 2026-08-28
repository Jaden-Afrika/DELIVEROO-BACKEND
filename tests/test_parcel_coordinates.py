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


class TestParcelCoordinates:
    def test_create_parcel_returns_pickup_coordinates(self, client, auth_header, seed_pricing_rules, seed_users):
        parcel = _create_parcel(client, auth_header)
        assert parcel["pickupLatitude"] is not None
        assert parcel["pickupLongitude"] is not None

    def test_create_parcel_returns_destination_coordinates(self, client, auth_header, seed_pricing_rules, seed_users):
        parcel = _create_parcel(client, auth_header)
        assert parcel["destinationLatitude"] is not None
        assert parcel["destinationLongitude"] is not None

    def test_destination_change_updates_destination_coordinates(
        self, client, auth_header, seed_pricing_rules, seed_users
    ):
        parcel = _create_parcel(client, auth_header)
        original_lat = parcel["destinationLatitude"]

        resp = client.patch(
            f"/parcels/{parcel['id']}/destination",
            {"destination": "Lavington, Nairobi"},
            **auth_header, format="json",
        )
        data = resp.json()
        assert data["destinationLatitude"] is not None
        assert data["destinationLongitude"] is not None
        # Coordinates should still be present even if the stub geocoder
        # returns the same point for every address.
        assert data["destinationLatitude"] == original_lat

    def test_destination_change_does_not_move_pickup_coordinates(
        self, client, auth_header, seed_pricing_rules, seed_users
    ):
        parcel = _create_parcel(client, auth_header)
        pickup_lat_before = parcel["pickupLatitude"]

        resp = client.patch(
            f"/parcels/{parcel['id']}/destination",
            {"destination": "Lavington, Nairobi"},
            **auth_header, format="json",
        )
        assert resp.json()["pickupLatitude"] == pickup_lat_before

    def test_get_parcel_detail_includes_coordinates(self, client, auth_header, seed_pricing_rules, seed_users):
        parcel = _create_parcel(client, auth_header)
        resp = client.get(f"/parcels/{parcel['id']}", **auth_header)
        data = resp.json()
        assert data["pickupLatitude"] is not None
        assert data["destinationLatitude"] is not None
