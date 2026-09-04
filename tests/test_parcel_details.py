import re

from django.urls import resolve

from app.models import Parcel
from app.models.enums import ParcelStatus


def _create_parcel(client, auth_header, **overrides):
    payload = {
        "pickupLocation": "Westlands, Nairobi",
        "destination": "Kilimani, Nairobi",
        "weightKg": 10,
        "distanceKm": 10.0,
    }
    payload.update(overrides)
    resp = client.post("/parcels", payload, **auth_header, format="json")
    return resp.json() if resp.status_code == 201 else None


ISO_RE = re.compile(r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}")


class TestGetParcelDetail:
    def test_owner_can_retrieve_parcel(self, client, auth_header, seed_pricing_rules, seed_users):
        parcel = _create_parcel(client, auth_header)
        resp = client.get(f"/parcels/{parcel['id']}", **auth_header)
        assert resp.status_code == 200
        data = resp.json()
        assert data["id"] == parcel["id"]
        assert data["pickupLocation"] == "Westlands, Nairobi"
        assert data["destination"] == "Kilimani, Nairobi"

    def test_unauthenticated_user_cannot_retrieve(self, client, auth_header, seed_pricing_rules, seed_users):
        parcel = _create_parcel(client, auth_header)
        resp = client.get(f"/parcels/{parcel['id']}")
        assert resp.status_code == 401

    def test_user_cannot_retrieve_other_users_parcel(self, client, auth_header, other_header, seed_pricing_rules, seed_users):
        parcel = _create_parcel(client, auth_header)
        resp = client.get(f"/parcels/{parcel['id']}", **other_header)
        assert resp.status_code == 404

    def test_admin_can_retrieve_any_parcel(self, client, auth_header, admin_header, seed_pricing_rules, seed_users):
        parcel = _create_parcel(client, auth_header)
        resp = client.get(f"/parcels/{parcel['id']}", **admin_header)
        assert resp.status_code == 200
        assert resp.json()["id"] == parcel["id"]

    def test_nonexistent_parcel_returns_404(self, client, auth_header, seed_pricing_rules, seed_users):
        resp = client.get("/parcels/99999", **auth_header)
        assert resp.status_code == 404

    def test_detail_contains_weight_and_vehicle_category(self, client, auth_header, seed_pricing_rules, seed_users):
        parcel = _create_parcel(client, auth_header, weightKg=51)
        resp = client.get(f"/parcels/{parcel['id']}", **auth_header)
        data = resp.json()
        assert data["weightKg"] == 51
        assert data["vehicleCategory"] == "lorry"

    def test_detail_contains_valid_created_at(self, client, auth_header, seed_pricing_rules, seed_users):
        parcel = _create_parcel(client, auth_header)
        resp = client.get(f"/parcels/{parcel['id']}", **auth_header)
        data = resp.json()
        assert ISO_RE.match(data["createdAt"]), f"Invalid createdAt: {data['createdAt']}"
        assert "Invalid Date" not in data["createdAt"]

    def test_detail_contains_date_created(self, client, auth_header, seed_pricing_rules, seed_users):
        parcel = _create_parcel(client, auth_header)
        resp = client.get(f"/parcels/{parcel['id']}", **auth_header)
        data = resp.json()
        assert ISO_RE.match(data["dateCreated"])

    def test_detail_contains_price_and_currency(self, client, auth_header, seed_pricing_rules, seed_users):
        parcel = _create_parcel(client, auth_header, weightKg=2, distanceKm=5.0)
        resp = client.get(f"/parcels/{parcel['id']}", **auth_header)
        data = resp.json()
        assert data["price"] == 300  # 150 + (15*5*2)
        assert data["currency"] == "KES"

    def test_detail_contains_estimated_travel_time(self, client, auth_header, seed_pricing_rules, seed_users):
        parcel = _create_parcel(client, auth_header, distanceKm=10.0)
        resp = client.get(f"/parcels/{parcel['id']}", **auth_header)
        data = resp.json()
        assert data["estimatedTravelTime"] == 15  # (10/40)*60 = 15

    def test_detail_contains_owner_info(self, client, auth_header, seed_pricing_rules, seed_users):
        parcel = _create_parcel(client, auth_header)
        resp = client.get(f"/parcels/{parcel['id']}", **auth_header)
        data = resp.json()
        assert "createdBy" in data
        assert "ownerId" in data
        assert "ownerName" in data
        assert data["ownerName"] == "Test User"


class TestUpdateDestination:
    def test_owner_can_change_destination(self, client, auth_header, seed_pricing_rules, seed_users):
        parcel = _create_parcel(client, auth_header)
        resp = client.patch(
            f"/parcels/{parcel['id']}/destination",
            {"destination": "Lavington, Nairobi"},
            **auth_header, format="json",
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["destination"] == "Lavington, Nairobi"

    def test_destination_change_updates_stored_value(self, client, auth_header, seed_pricing_rules, seed_users):
        parcel = _create_parcel(client, auth_header)
        client.patch(
            f"/parcels/{parcel['id']}/destination",
            {"destination": "Karen, Nairobi"},
            **auth_header, format="json",
        )
        resp = client.get(f"/parcels/{parcel['id']}", **auth_header)
        assert resp.json()["destination"] == "Karen, Nairobi"

    def test_destination_change_returns_complete_parcel(self, client, auth_header, seed_pricing_rules, seed_users):
        parcel = _create_parcel(client, auth_header)
        resp = client.patch(
            f"/parcels/{parcel['id']}/destination",
            {"destination": "South B, Nairobi"},
            **auth_header, format="json",
        )
        data = resp.json()
        assert "id" in data
        assert "status" in data
        assert "pickupLocation" in data
        assert "destination" in data
        assert "price" in data

    def test_delivered_parcel_cannot_change_destination(self, client, auth_header, seed_pricing_rules, seed_users):
        parcel = _create_parcel(client, auth_header)
        p = Parcel.objects.get(pk=parcel["id"])
        p.status = ParcelStatus.delivered.value
        p.save()

        resp = client.patch(
            f"/parcels/{parcel['id']}/destination",
            {"destination": "New Place"},
            **auth_header, format="json",
        )
        assert resp.status_code == 409
        assert resp.json()["error"]["code"] == "PARCEL_DELIVERED"

    def test_cancelled_parcel_cannot_change_destination(self, client, auth_header, seed_pricing_rules, seed_users):
        parcel = _create_parcel(client, auth_header)
        client.patch(f"/parcels/{parcel['id']}/cancel", **auth_header, format="json")

        resp = client.patch(
            f"/parcels/{parcel['id']}/destination",
            {"destination": "New Place"},
            **auth_header, format="json",
        )
        assert resp.status_code == 409
        assert resp.json()["error"]["code"] == "PARCEL_CANCELLED"

    def test_empty_destination_rejected(self, client, auth_header, seed_pricing_rules, seed_users):
        parcel = _create_parcel(client, auth_header)
        resp = client.patch(
            f"/parcels/{parcel['id']}/destination",
            {"destination": ""},
            **auth_header, format="json",
        )
        assert resp.status_code == 400
        assert resp.json()["error"]["code"] == "INVALID_DESTINATION"
        assert "details" in resp.json()["error"]

    def test_non_owner_cannot_change_destination(self, client, auth_header, other_header, seed_pricing_rules, seed_users):
        parcel = _create_parcel(client, auth_header)
        resp = client.patch(
            f"/parcels/{parcel['id']}/destination",
            {"destination": "New Place"},
            **other_header, format="json",
        )
        assert resp.status_code == 403

    def test_same_destination_no_change(self, client, auth_header, seed_pricing_rules, seed_users):
        parcel = _create_parcel(client, auth_header)
        resp = client.patch(
            f"/parcels/{parcel['id']}/destination",
            {"destination": "Kilimani, Nairobi"},
            **auth_header, format="json",
        )
        assert resp.status_code == 200
        assert resp.json()["destination"] == "Kilimani, Nairobi"


class TestCancelParcel:
    def test_owner_can_cancel(self, client, auth_header, seed_pricing_rules, seed_users):
        parcel = _create_parcel(client, auth_header)
        resp = client.patch(f"/parcels/{parcel['id']}/cancel", **auth_header, format="json")
        assert resp.status_code == 200
        data = resp.json()
        assert data["status"] == "cancelled"

    def test_cancellation_returns_cancelled_at(self, client, auth_header, seed_pricing_rules, seed_users):
        parcel = _create_parcel(client, auth_header)
        resp = client.patch(f"/parcels/{parcel['id']}/cancel", **auth_header, format="json")
        data = resp.json()
        assert "cancelledAt" in data
        assert ISO_RE.match(data["cancelledAt"])

    def test_cancellation_persists_after_fresh_get(self, client, auth_header, seed_pricing_rules, seed_users):
        parcel = _create_parcel(client, auth_header)
        client.patch(f"/parcels/{parcel['id']}/cancel", **auth_header, format="json")
        resp = client.get(f"/parcels/{parcel['id']}", **auth_header)
        assert resp.json()["status"] == "cancelled"

    def test_cancellation_appears_in_list(self, client, auth_header, seed_pricing_rules, seed_users):
        parcel = _create_parcel(client, auth_header)
        client.patch(f"/parcels/{parcel['id']}/cancel", **auth_header, format="json")
        resp = client.get("/parcels/me", **auth_header)
        parcels = resp.json()
        cancelled = [p for p in parcels if p["id"] == parcel["id"]]
        assert len(cancelled) == 1
        assert cancelled[0]["status"] == "cancelled"

    def test_delivered_parcel_cannot_be_cancelled(self, client, auth_header, seed_pricing_rules, seed_users):
        parcel = _create_parcel(client, auth_header)
        p = Parcel.objects.get(pk=parcel["id"])
        p.status = ParcelStatus.delivered.value
        p.save()

        resp = client.patch(f"/parcels/{parcel['id']}/cancel", **auth_header, format="json")
        assert resp.status_code == 409
        assert resp.json()["error"]["code"] == "PARCEL_DELIVERED"

    def test_cancelled_parcel_cannot_be_cancelled_again(self, client, auth_header, seed_pricing_rules, seed_users):
        parcel = _create_parcel(client, auth_header)
        client.patch(f"/parcels/{parcel['id']}/cancel", **auth_header, format="json")
        resp = client.patch(f"/parcels/{parcel['id']}/cancel", **auth_header, format="json")
        assert resp.status_code == 409
        assert resp.json()["error"]["code"] == "PARCEL_CANCELLED"

    def test_non_owner_cannot_cancel(self, client, auth_header, other_header, seed_pricing_rules, seed_users):
        parcel = _create_parcel(client, auth_header)
        resp = client.patch(f"/parcels/{parcel['id']}/cancel", **other_header, format="json")
        assert resp.status_code == 404

    def test_status_history_created_on_cancel(self, client, auth_header, seed_pricing_rules, seed_users):
        parcel = _create_parcel(client, auth_header)
        client.patch(f"/parcels/{parcel['id']}/cancel", **auth_header, format="json")

        resp = client.get(f"/parcels/{parcel['id']}/status-history", **auth_header)
        history = resp.json()
        cancelled_entries = [h for h in history if h["status"] == "cancelled"]
        assert len(cancelled_entries) >= 1

    def test_status_history_on_create(self, client, auth_header, seed_pricing_rules, seed_users):
        parcel = _create_parcel(client, auth_header)
        resp = client.get(f"/parcels/{parcel['id']}/status-history", **auth_header)
        history = resp.json()
        assert len(history) >= 1
        assert history[0]["status"] == "pending"


class TestRouteRegistration:
    def test_parcel_detail_routes_registered(self):
        assert resolve("/parcels/1")
        assert resolve("/parcels/1/destination")
        assert resolve("/parcels/1/cancel")
        assert resolve("/parcels/1/status-history")

    def test_openapi_reflects_endpoints(self, client):
        resp = client.get("/openapi.json")
        spec = resp.json()
        assert "/parcels/{id}" in spec["paths"]
        assert "/parcels/{id}/destination" in spec["paths"]
        assert "/parcels/{id}/cancel" in spec["paths"]
