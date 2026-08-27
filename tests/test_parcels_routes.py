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
