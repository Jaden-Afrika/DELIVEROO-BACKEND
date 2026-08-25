class TestAdminListParcels:
    def test_admin_list(self, client, admin_header):
        resp = client.get("/admin/parcels", headers=admin_header)
        assert resp.status_code == 200

    def test_non_admin_rejected(self, client, auth_header):
        resp = client.get("/admin/parcels", headers=auth_header)
        assert resp.status_code == 403

    def test_unauthenticated_rejected(self, client):
        resp = client.get("/admin/parcels")
        assert resp.status_code == 401


class TestAdminUpdateStatus:
    def test_update_status(self, client, admin_header, auth_header, seed_pricing_rules, seed_users):
        create_resp = client.post("/parcels", headers=auth_header, json={
            "pickupLocation": "A", "destination": "B",
            "weightCategory": "light", "distanceKm": 5,
        })
        parcel_id = create_resp.get_json()["id"]
        resp = client.patch(
            f"/admin/parcels/{parcel_id}/status",
            headers=admin_header,
            json={"status": "in_transit"},
        )
        assert resp.status_code == 200
        assert resp.get_json()["status"] == "in_transit"

    def test_non_admin_cannot_update(self, client, auth_header, seed_pricing_rules, seed_users):
        create_resp = client.post("/parcels", headers=auth_header, json={
            "pickupLocation": "A", "destination": "B",
            "weightCategory": "light", "distanceKm": 5,
        })
        parcel_id = create_resp.get_json()["id"]
        resp = client.patch(
            f"/admin/parcels/{parcel_id}/status",
            headers=auth_header,
            json={"status": "in_transit"},
        )
        assert resp.status_code == 403


class TestAdminUpdateLocation:
    def test_update_location(self, client, admin_header, auth_header, seed_pricing_rules, seed_users):
        create_resp = client.post("/parcels", headers=auth_header, json={
            "pickupLocation": "A", "destination": "B",
            "weightCategory": "light", "distanceKm": 5,
        })
        parcel_id = create_resp.get_json()["id"]
        resp = client.patch(
            f"/admin/parcels/{parcel_id}/location",
            headers=admin_header,
            json={"currentLocation": "Museum Hill, Nairobi"},
        )
        assert resp.status_code == 200
        assert resp.get_json()["currentLocation"] == "Museum Hill, Nairobi"
