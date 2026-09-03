class TestAdminListParcels:
    def test_admin_list(self, client, admin_header):
        resp = client.get("/admin/parcels", **admin_header)
        assert resp.status_code == 200

    def test_non_admin_rejected(self, client, auth_header):
        resp = client.get("/admin/parcels", **auth_header)
        assert resp.status_code == 403

    def test_unauthenticated_rejected(self, client):
        resp = client.get("/admin/parcels")
        assert resp.status_code == 401


class TestAdminUpdateStatus:
    def test_update_status(self, client, admin_header, auth_header, seed_pricing_rules, seed_users):
        create_resp = client.post("/parcels", {
            "pickupLocation": "A", "destination": "B",
            "weightKg": 2, "distanceKm": 5,
        }, **auth_header, format="json")
        parcel_id = create_resp.json()["id"]
        resp = client.patch(
            f"/admin/parcels/{parcel_id}/status",
            {"status": "in_transit"},
            **admin_header, format="json",
        )
        assert resp.status_code == 200
        assert resp.json()["status"] == "in_transit"

    def test_non_admin_cannot_update(self, client, auth_header, seed_pricing_rules, seed_users):
        create_resp = client.post("/parcels", {
            "pickupLocation": "A", "destination": "B",
            "weightKg": 2, "distanceKm": 5,
        }, **auth_header, format="json")
        parcel_id = create_resp.json()["id"]
        resp = client.patch(
            f"/admin/parcels/{parcel_id}/status",
            {"status": "in_transit"},
            **auth_header, format="json",
        )
        assert resp.status_code == 403


class TestAdminUpdateLocation:
    def test_update_location(self, client, admin_header, auth_header, seed_pricing_rules, seed_users):
        create_resp = client.post("/parcels", {
            "pickupLocation": "A", "destination": "B",
            "weightKg": 2, "distanceKm": 5,
        }, **auth_header, format="json")
        parcel_id = create_resp.json()["id"]
        resp = client.patch(
            f"/admin/parcels/{parcel_id}/location",
            {"currentLocation": "Museum Hill, Nairobi"},
            **admin_header, format="json",
        )
        assert resp.status_code == 200
        assert resp.json()["currentLocation"] == "Museum Hill, Nairobi"
