class TestCreateParcel:
    def test_create_parcel(self, client, auth_header, seed_pricing_rules, seed_users):
        resp = client.post("/parcels", {
            "pickupLocation": "Westlands, Nairobi",
            "destination": "Kilimani, Nairobi",
            "weightKg": 10,
            "distanceKm": 10.0,
        }, **auth_header, format="json")
        assert resp.status_code == 201
        data = resp.json()
        assert data["pickupLocation"] == "Westlands, Nairobi"
        assert data["destination"] == "Kilimani, Nairobi"
        assert data["weightKg"] == 10
        assert data["vehicleCategory"] == "car"
        assert data["price"] == 1650  # 150 + (15*10*10)
        assert data["status"] == "pending"
        assert "id" in data

    def test_create_parcel_unauthenticated(self, client, seed_pricing_rules):
        resp = client.post("/parcels", {
            "pickupLocation": "A", "destination": "B",
            "weightKg": 2, "distanceKm": 5,
        }, format="json")
        assert resp.status_code == 401

    def test_vehicle_category_is_derived_at_weight_thresholds(self, client, auth_header, seed_pricing_rules, seed_users):
        for weight_kg, vehicle_category in ((5.0, "bike"), (5.01, "car"), (50.0, "car"), (50.01, "lorry")):
            resp = client.post("/parcels", {
                "pickupLocation": "A",
                "destination": "B",
                "weightKg": weight_kg,
                "distanceKm": 5,
                # A client-supplied category is deliberately ignored.
                "vehicleCategory": "bike",
            }, **auth_header, format="json")
            assert resp.status_code == 201
            assert resp.json()["vehicleCategory"] == vehicle_category

    def test_frontend_weight_contract_is_accepted_and_category_is_server_derived(
        self, client, auth_header, seed_pricing_rules, seed_users
    ):
        resp = client.post("/parcels", {
            "pickupLocation": "A",
            "destination": "B",
            "weight": 50.01,
            "vehicle_category": "bike",
            "distanceKm": 5,
        }, **auth_header, format="json")

        assert resp.status_code == 201
        assert resp.json()["weight"] == 50.01
        assert resp.json()["vehicle_category"] == "lorry"

    def test_vehicle_category_is_present_in_list_and_admin_responses(
        self, client, auth_header, admin_header, seed_pricing_rules, seed_users
    ):
        created = client.post("/parcels", {
            "pickupLocation": "A", "destination": "B", "weightKg": 2, "distanceKm": 5,
        }, **auth_header, format="json").json()

        mine = client.get("/parcels/me", **auth_header).json()
        admin = client.get("/admin/parcels", **admin_header).json()
        assert mine[0]["vehicleCategory"] == "bike"
        assert next(parcel for parcel in admin if parcel["id"] == created["id"])["vehicleCategory"] == "bike"


class TestListMyParcels:
    def test_list_empty(self, client, auth_header):
        resp = client.get("/parcels/me", **auth_header)
        assert resp.status_code == 200
        assert resp.json() == []

    def test_list_with_parcels(self, client, auth_header, seed_pricing_rules, seed_users):
        client.post("/parcels", {
            "pickupLocation": "A", "destination": "B",
            "weightKg": 2, "distanceKm": 5,
        }, **auth_header, format="json")
        resp = client.get("/parcels/me", **auth_header)
        assert resp.status_code == 200
        assert len(resp.json()) == 1


class TestCancelParcel:
    def test_cancel_own_parcel(self, client, auth_header, seed_pricing_rules, seed_users):
        create_resp = client.post("/parcels", {
            "pickupLocation": "A", "destination": "B",
            "weightKg": 2, "distanceKm": 5,
        }, **auth_header, format="json")
        parcel_id = create_resp.json()["id"]
        resp = client.patch(f"/parcels/{parcel_id}/cancel", **auth_header, format="json")
        assert resp.status_code == 200
        assert resp.json()["status"] == "cancelled"

    def test_cancel_other_users_parcel(self, client, auth_header, other_header, seed_pricing_rules, seed_users):
        create_resp = client.post("/parcels", {
            "pickupLocation": "A", "destination": "B",
            "weightKg": 2, "distanceKm": 5,
        }, **auth_header, format="json")
        parcel_id = create_resp.json()["id"]
        resp = client.patch(f"/parcels/{parcel_id}/cancel", **other_header, format="json")
        assert resp.status_code == 404

    def test_cancel_already_delivered_parcel(self, client, auth_header, admin_header, seed_pricing_rules, seed_users):
        create_resp = client.post("/parcels", {
            "pickupLocation": "A", "destination": "B",
            "weightKg": 2, "distanceKm": 5,
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
            "weightKg": 2, "distanceKm": 5,
        }, **auth_header, format="json")
        parcel_id = create_resp.json()["id"]
        resp = client.get(f"/parcels/{parcel_id}", **auth_header)
        assert resp.status_code == 200
        assert resp.json()["id"] == parcel_id

    def test_get_other_users_parcel(self, client, auth_header, other_header, seed_pricing_rules, seed_users):
        create_resp = client.post("/parcels", {
            "pickupLocation": "A", "destination": "B",
            "weightKg": 2, "distanceKm": 5,
        }, **auth_header, format="json")
        parcel_id = create_resp.json()["id"]
        resp = client.get(f"/parcels/{parcel_id}", **other_header)
        assert resp.status_code == 404


class TestUpdateDestination:
    def test_update_own_parcel_destination(self, client, auth_header, seed_pricing_rules, seed_users):
        create_resp = client.post("/parcels", {
            "pickupLocation": "A", "destination": "B",
            "weightKg": 2, "distanceKm": 5,
        }, **auth_header, format="json")
        parcel_id = create_resp.json()["id"]
        resp = client.patch(
            f"/parcels/{parcel_id}/destination",
            {"destination": "New Destination"},
            **auth_header,
            format="json",
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["destination"] == "New Destination"
        assert data["distanceKm"] == 10.0
        assert data["estimatedTravelTime"] == 25
        assert data["price"] == 450
        assert data["destinationLatitude"] == -1.2921
        assert data["destinationLongitude"] == 36.8219

    def test_update_other_users_parcel_destination(self, client, auth_header, other_header, seed_pricing_rules, seed_users):
        create_resp = client.post("/parcels", {
            "pickupLocation": "A", "destination": "B",
            "weightKg": 2, "distanceKm": 5,
        }, **auth_header, format="json")
        parcel_id = create_resp.json()["id"]
        resp = client.patch(
            f"/parcels/{parcel_id}/destination",
            {"destination": "Hijacked"},
            **other_header,
            format="json",
        )
        assert resp.status_code == 403

    def test_update_missing_parcel_destination(self, client, auth_header, seed_users):
        resp = client.patch(
            "/parcels/99999/destination",
            {"destination": "New Destination"},
            **auth_header,
            format="json",
        )
        assert resp.status_code == 404

    def test_update_destination_rejects_blank_value(self, client, auth_header, seed_pricing_rules, seed_users):
        create_resp = client.post("/parcels", {
            "pickupLocation": "A", "destination": "B",
            "weightKg": 2, "distanceKm": 5,
        }, **auth_header, format="json")
        resp = client.patch(
            f"/parcels/{create_resp.json()['id']}/destination",
            {"destination": "   "},
            **auth_header,
            format="json",
        )
        assert resp.status_code == 400

    def test_update_destination_rejects_unresolvable_value(self, client, auth_header, seed_pricing_rules, seed_users, monkeypatch):
        from app import views

        create_resp = client.post("/parcels", {
            "pickupLocation": "A", "destination": "B",
            "weightKg": 2, "distanceKm": 5,
        }, **auth_header, format="json")
        monkeypatch.setattr(views.get_geocoding_service(), "geocode", lambda value: None)
        resp = client.patch(
            f"/parcels/{create_resp.json()['id']}/destination",
            {"destination": "Unknown Place"},
            **auth_header,
            format="json",
        )
        assert resp.status_code == 400

    def test_update_destination_on_delivered_parcel(self, client, auth_header, admin_header, seed_pricing_rules, seed_users):
        create_resp = client.post("/parcels", {
            "pickupLocation": "A", "destination": "B",
            "weightKg": 2, "distanceKm": 5,
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

    def test_update_destination_on_cancelled_parcel(self, client, auth_header, seed_pricing_rules, seed_users):
        create_resp = client.post("/parcels", {
            "pickupLocation": "A", "destination": "B",
            "weightKg": 2, "distanceKm": 5,
        }, **auth_header, format="json")
        parcel_id = create_resp.json()["id"]
        client.patch(f"/parcels/{parcel_id}/cancel", **auth_header, format="json")

        resp = client.patch(
            f"/parcels/{parcel_id}/destination",
            {"destination": "Too Late"},
            **auth_header,
            format="json",
        )
        assert resp.status_code == 409
