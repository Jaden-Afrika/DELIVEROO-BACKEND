class TestCreateParcel:
    def test_create_parcel(self, client, auth_header, seed_pricing_rules, seed_users):
        resp = client.post("/parcels", {
            "pickupLocation": "Westlands, Nairobi",
            "destination": "Kilimani, Nairobi",
            "weightCategory": "medium",
            "distanceKm": 10.0,
        }, **auth_header, format="json")
        assert resp.status_code == 201
        data = resp.json()
        assert data["pickupLocation"] == "Westlands, Nairobi"
        assert data["destination"] == "Kilimani, Nairobi"
        assert data["weightCategory"] == "medium"
        assert data["price"] == 600  # 350 + 25*10
        assert data["status"] == "pending"
        assert "id" in data

    def test_create_parcel_unauthenticated(self, client, seed_pricing_rules):
        resp = client.post("/parcels", {
            "pickupLocation": "A", "destination": "B",
            "weightCategory": "light", "distanceKm": 5,
        }, format="json")
        assert resp.status_code == 401


class TestListMyParcels:
    def test_list_empty(self, client, auth_header):
        resp = client.get("/parcels/me", **auth_header)
        assert resp.status_code == 200
        assert resp.json() == []

    def test_list_with_parcels(self, client, auth_header, seed_pricing_rules, seed_users):
        client.post("/parcels", {
            "pickupLocation": "A", "destination": "B",
            "weightCategory": "light", "distanceKm": 5,
        }, **auth_header, format="json")
        resp = client.get("/parcels/me", **auth_header)
        assert resp.status_code == 200
        assert len(resp.json()) == 1


class TestCancelParcel:
    def test_cancel_own_parcel(self, client, auth_header, seed_pricing_rules, seed_users):
        create_resp = client.post("/parcels", {
            "pickupLocation": "A", "destination": "B",
            "weightCategory": "light", "distanceKm": 5,
        }, **auth_header, format="json")
        parcel_id = create_resp.json()["id"]
        resp = client.patch(f"/parcels/{parcel_id}/cancel", **auth_header, format="json")
        assert resp.status_code == 200
        assert resp.json()["status"] == "cancelled"

    def test_cancel_other_users_parcel(self, client, auth_header, other_header, seed_pricing_rules, seed_users):
        create_resp = client.post("/parcels", {
            "pickupLocation": "A", "destination": "B",
            "weightCategory": "light", "distanceKm": 5,
        }, **auth_header, format="json")
        parcel_id = create_resp.json()["id"]
        resp = client.patch(f"/parcels/{parcel_id}/cancel", **other_header, format="json")
        assert resp.status_code == 404

    def test_cancel_already_delivered_parcel(self, client, auth_header, admin_header, seed_pricing_rules, seed_users):
        create_resp = client.post("/parcels", {
            "pickupLocation": "A", "destination": "B",
            "weightCategory": "light", "distanceKm": 5,
        }, **auth_header, format="json")
        parcel_id = create_resp.json()["id"]
        # admin marks it delivered first
        client.patch(
            f"/admin/parcels/{parcel_id}/status",
            {"status": "delivered"},
            **admin_header,
            format="json",
        )

        resp = client.patch(f"/parcels/{parcel_id}/cancel", **auth_header, format="json")
        assert resp.status_code == 409

        # confirm it's genuinely unchanged, not just that the error was returned
        check = client.get(f"/parcels/{parcel_id}", **auth_header)
        assert check.json()["status"] == "delivered"


class TestGetParcel:
    def test_get_own_parcel(self, client, auth_header, seed_pricing_rules, seed_users):
        create_resp = client.post("/parcels", {
            "pickupLocation": "A", "destination": "B",
            "weightCategory": "light", "distanceKm": 5,
        }, **auth_header, format="json")
        parcel_id = create_resp.json()["id"]
        resp = client.get(f"/parcels/{parcel_id}", **auth_header)
        assert resp.status_code == 200
        assert resp.json()["id"] == parcel_id

    def test_get_other_users_parcel(self, client, auth_header, other_header, seed_pricing_rules, seed_users):
        create_resp = client.post("/parcels", {
            "pickupLocation": "A", "destination": "B",
            "weightCategory": "light", "distanceKm": 5,
        }, **auth_header, format="json")
        parcel_id = create_resp.json()["id"]
        resp = client.get(f"/parcels/{parcel_id}", **other_header)
        assert resp.status_code == 404


class TestUpdateDestination:
    def test_update_own_parcel_destination(self, client, auth_header, seed_pricing_rules, seed_users):
        create_resp = client.post("/parcels", {
            "pickupLocation": "A", "destination": "B",
            "weightCategory": "light", "distanceKm": 5,
        }, **auth_header, format="json")
        parcel_id = create_resp.json()["id"]
        resp = client.patch(
            f"/parcels/{parcel_id}/destination",
            {"destination": "New Destination"},
            **auth_header,
            format="json",
        )
        assert resp.status_code == 200
        assert resp.json()["destination"] == "New Destination"

    def test_update_other_users_parcel_destination(self, client, auth_header, other_header, seed_pricing_rules, seed_users):
        create_resp = client.post("/parcels", {
            "pickupLocation": "A", "destination": "B",
            "weightCategory": "light", "distanceKm": 5,
        }, **auth_header, format="json")
        parcel_id = create_resp.json()["id"]
        resp = client.patch(
            f"/parcels/{parcel_id}/destination",
            {"destination": "Hijacked"},
            **other_header,
            format="json",
        )
        assert resp.status_code == 404

    def test_update_destination_on_delivered_parcel(self, client, auth_header, admin_header, seed_pricing_rules, seed_users):
        create_resp = client.post("/parcels", {
            "pickupLocation": "A", "destination": "B",
            "weightCategory": "light", "distanceKm": 5,
        }, **auth_header, format="json")
        parcel_id = create_resp.json()["id"]
        client.patch(
            f"/admin/parcels/{parcel_id}/status",
            {"status": "delivered"},
            **admin_header,
            format="json",
        )

        resp = client.patch(
            f"/parcels/{parcel_id}/destination",
            {"destination": "Too Late"},
            **auth_header,
            format="json",
        )
        assert resp.status_code == 409

        check = client.get(f"/parcels/{parcel_id}", **auth_header)
        assert check.json()["destination"] == "B"  # unchanged
