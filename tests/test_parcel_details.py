import re
from datetime import datetime, timezone

from app.extensions import db
from app.models.parcel import Parcel
from app.models.parcel_status_history import ParcelStatusHistory
from app.models.enums import ParcelStatus


def _create_parcel(client, auth_header, **overrides):
    payload = {
        "pickupLocation": "Westlands, Nairobi",
        "destination": "Kilimani, Nairobi",
        "weightCategory": "medium",
        "distanceKm": 10.0,
    }
    payload.update(overrides)
    resp = client.post("/parcels", headers=auth_header, json=payload)
    return resp.get_json() if resp.status_code == 201 else None


ISO_RE = re.compile(r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}")


# ─── GET /parcels/<id> ──────────────────────────────────────────────


class TestGetParcelDetail:
    def test_owner_can_retrieve_parcel(self, client, auth_header, seed_pricing_rules, seed_users):
        parcel = _create_parcel(client, auth_header)
        resp = client.get(f"/parcels/{parcel['id']}", headers=auth_header)
        assert resp.status_code == 200
        data = resp.get_json()
        assert data["id"] == parcel["id"]
        assert data["pickupLocation"] == "Westlands, Nairobi"
        assert data["destination"] == "Kilimani, Nairobi"

    def test_unauthenticated_user_cannot_retrieve(self, client, auth_header, seed_pricing_rules, seed_users):
        parcel = _create_parcel(client, auth_header)
        resp = client.get(f"/parcels/{parcel['id']}")
        assert resp.status_code == 401

    def test_user_cannot_retrieve_other_users_parcel(self, client, auth_header, other_header, seed_pricing_rules, seed_users):
        parcel = _create_parcel(client, auth_header)
        resp = client.get(f"/parcels/{parcel['id']}", headers=other_header)
        assert resp.status_code == 404

    def test_admin_can_retrieve_any_parcel(self, client, auth_header, admin_header, seed_pricing_rules, seed_users):
        parcel = _create_parcel(client, auth_header)
        resp = client.get(f"/parcels/{parcel['id']}", headers=admin_header)
        assert resp.status_code == 200
        assert resp.get_json()["id"] == parcel["id"]

    def test_nonexistent_parcel_returns_404(self, client, auth_header, seed_pricing_rules, seed_users):
        resp = client.get("/parcels/99999", headers=auth_header)
        assert resp.status_code == 404

    def test_detail_contains_weight_category(self, client, auth_header, seed_pricing_rules, seed_users):
        parcel = _create_parcel(client, auth_header, weightCategory="heavy")
        resp = client.get(f"/parcels/{parcel['id']}", headers=auth_header)
        data = resp.get_json()
        assert data["weightCategory"] == "heavy"
        assert "Heavy" in data["weight"]

    def test_detail_contains_valid_created_at(self, client, auth_header, seed_pricing_rules, seed_users):
        parcel = _create_parcel(client, auth_header)
        resp = client.get(f"/parcels/{parcel['id']}", headers=auth_header)
        data = resp.get_json()
        assert ISO_RE.match(data["createdAt"]), f"Invalid createdAt: {data['createdAt']}"
        assert "Invalid Date" not in data["createdAt"]

    def test_detail_contains_date_created(self, client, auth_header, seed_pricing_rules, seed_users):
        parcel = _create_parcel(client, auth_header)
        resp = client.get(f"/parcels/{parcel['id']}", headers=auth_header)
        data = resp.get_json()
        assert ISO_RE.match(data["dateCreated"])

    def test_detail_contains_price_and_currency(self, client, auth_header, seed_pricing_rules, seed_users):
        parcel = _create_parcel(client, auth_header, weightCategory="light", distanceKm=5.0)
        resp = client.get(f"/parcels/{parcel['id']}", headers=auth_header)
        data = resp.get_json()
        assert data["price"] == 225  # 150 + 15*5
        assert data["currency"] == "KES"

    def test_detail_contains_estimated_travel_time(self, client, auth_header, seed_pricing_rules, seed_users):
        parcel = _create_parcel(client, auth_header, distanceKm=10.0)
        resp = client.get(f"/parcels/{parcel['id']}", headers=auth_header)
        data = resp.get_json()
        assert data["estimatedTravelTime"] == 15  # (10/40)*60 = 15

    def test_detail_contains_owner_info(self, client, auth_header, seed_pricing_rules, seed_users):
        parcel = _create_parcel(client, auth_header)
        resp = client.get(f"/parcels/{parcel['id']}", headers=auth_header)
        data = resp.get_json()
        assert "createdBy" in data
        assert "ownerId" in data
        assert "ownerName" in data
        assert data["ownerName"] == "Test User"


# ─── PATCH /parcels/<id>/destination ─────────────────────────────────


class TestUpdateDestination:
    def test_owner_can_change_destination(self, client, auth_header, seed_pricing_rules, seed_users):
        parcel = _create_parcel(client, auth_header)
        resp = client.patch(
            f"/parcels/{parcel['id']}/destination",
            headers=auth_header,
            json={"destination": "Lavington, Nairobi"},
        )
        assert resp.status_code == 200
        data = resp.get_json()
        assert data["destination"] == "Lavington, Nairobi"

    def test_destination_change_updates_stored_value(self, client, auth_header, seed_pricing_rules, seed_users):
        parcel = _create_parcel(client, auth_header)
        client.patch(
            f"/parcels/{parcel['id']}/destination",
            headers=auth_header,
            json={"destination": "Karen, Nairobi"},
        )
        resp = client.get(f"/parcels/{parcel['id']}", headers=auth_header)
        assert resp.get_json()["destination"] == "Karen, Nairobi"

    def test_destination_change_returns_complete_parcel(self, client, auth_header, seed_pricing_rules, seed_users):
        parcel = _create_parcel(client, auth_header)
        resp = client.patch(
            f"/parcels/{parcel['id']}/destination",
            headers=auth_header,
            json={"destination": "South B, Nairobi"},
        )
        data = resp.get_json()
        assert "id" in data
        assert "status" in data
        assert "pickupLocation" in data
        assert "destination" in data
        assert "price" in data

    def test_delivered_parcel_cannot_change_destination(self, client, auth_header, seed_pricing_rules, seed_users):
        parcel = _create_parcel(client, auth_header)
        db.session = db.session
        p = db.session.get(Parcel, parcel["id"])
        p.status = ParcelStatus.delivered
        db.session.commit()

        resp = client.patch(
            f"/parcels/{parcel['id']}/destination",
            headers=auth_header,
            json={"destination": "New Place"},
        )
        assert resp.status_code == 409
        assert resp.get_json()["error"]["code"] == "PARCEL_DELIVERED"

    def test_cancelled_parcel_cannot_change_destination(self, client, auth_header, seed_pricing_rules, seed_users):
        parcel = _create_parcel(client, auth_header)
        client.patch(f"/parcels/{parcel['id']}/cancel", headers=auth_header)

        resp = client.patch(
            f"/parcels/{parcel['id']}/destination",
            headers=auth_header,
            json={"destination": "New Place"},
        )
        assert resp.status_code == 409
        assert resp.get_json()["error"]["code"] == "PARCEL_CANCELLED"

    def test_empty_destination_rejected(self, client, auth_header, seed_pricing_rules, seed_users):
        parcel = _create_parcel(client, auth_header)
        resp = client.patch(
            f"/parcels/{parcel['id']}/destination",
            headers=auth_header,
            json={"destination": ""},
        )
        assert resp.status_code == 422

    def test_non_owner_cannot_change_destination(self, client, auth_header, other_header, seed_pricing_rules, seed_users):
        parcel = _create_parcel(client, auth_header)
        resp = client.patch(
            f"/parcels/{parcel['id']}/destination",
            headers=other_header,
            json={"destination": "New Place"},
        )
        assert resp.status_code == 404

    def test_same_destination_no_change(self, client, auth_header, seed_pricing_rules, seed_users):
        parcel = _create_parcel(client, auth_header)
        resp = client.patch(
            f"/parcels/{parcel['id']}/destination",
            headers=auth_header,
            json={"destination": "Kilimani, Nairobi"},
        )
        assert resp.status_code == 200
        assert resp.get_json()["destination"] == "Kilimani, Nairobi"


# ─── PATCH /parcels/<id>/cancel ──────────────────────────────────────


class TestCancelParcel:
    def test_owner_can_cancel(self, client, auth_header, seed_pricing_rules, seed_users):
        parcel = _create_parcel(client, auth_header)
        resp = client.patch(f"/parcels/{parcel['id']}/cancel", headers=auth_header)
        assert resp.status_code == 200
        data = resp.get_json()
        assert data["status"] == "cancelled"

    def test_cancellation_returns_cancelled_at(self, client, auth_header, seed_pricing_rules, seed_users):
        parcel = _create_parcel(client, auth_header)
        resp = client.patch(f"/parcels/{parcel['id']}/cancel", headers=auth_header)
        data = resp.get_json()
        assert "cancelledAt" in data
        assert ISO_RE.match(data["cancelledAt"])

    def test_cancellation_persists_after_fresh_get(self, client, auth_header, seed_pricing_rules, seed_users):
        parcel = _create_parcel(client, auth_header)
        client.patch(f"/parcels/{parcel['id']}/cancel", headers=auth_header)
        resp = client.get(f"/parcels/{parcel['id']}", headers=auth_header)
        assert resp.get_json()["status"] == "cancelled"

    def test_cancellation_appears_in_list(self, client, auth_header, seed_pricing_rules, seed_users):
        parcel = _create_parcel(client, auth_header)
        client.patch(f"/parcels/{parcel['id']}/cancel", headers=auth_header)
        resp = client.get("/parcels/me", headers=auth_header)
        parcels = resp.get_json()
        cancelled = [p for p in parcels if p["id"] == parcel["id"]]
        assert len(cancelled) == 1
        assert cancelled[0]["status"] == "cancelled"

    def test_delivered_parcel_cannot_be_cancelled(self, client, auth_header, seed_pricing_rules, seed_users):
        parcel = _create_parcel(client, auth_header)
        p = db.session.get(Parcel, parcel["id"])
        p.status = ParcelStatus.delivered
        db.session.commit()

        resp = client.patch(f"/parcels/{parcel['id']}/cancel", headers=auth_header)
        assert resp.status_code == 409
        assert resp.get_json()["error"]["code"] == "PARCEL_DELIVERED"

    def test_cancelled_parcel_cannot_be_cancelled_again(self, client, auth_header, seed_pricing_rules, seed_users):
        parcel = _create_parcel(client, auth_header)
        client.patch(f"/parcels/{parcel['id']}/cancel", headers=auth_header)
        resp = client.patch(f"/parcels/{parcel['id']}/cancel", headers=auth_header)
        assert resp.status_code == 409
        assert resp.get_json()["error"]["code"] == "PARCEL_CANCELLED"

    def test_non_owner_cannot_cancel(self, client, auth_header, other_header, seed_pricing_rules, seed_users):
        parcel = _create_parcel(client, auth_header)
        resp = client.patch(f"/parcels/{parcel['id']}/cancel", headers=other_header)
        assert resp.status_code == 404

    def test_status_history_created_on_cancel(self, client, auth_header, seed_pricing_rules, seed_users):
        parcel = _create_parcel(client, auth_header)
        client.patch(f"/parcels/{parcel['id']}/cancel", headers=auth_header)

        resp = client.get(f"/parcels/{parcel['id']}/status-history", headers=auth_header)
        history = resp.get_json()
        cancelled_entries = [h for h in history if h["status"] == "cancelled"]
        assert len(cancelled_entries) >= 1

    def test_status_history_on_create(self, client, auth_header, seed_pricing_rules, seed_users):
        parcel = _create_parcel(client, auth_header)
        resp = client.get(f"/parcels/{parcel['id']}/status-history", headers=auth_header)
        history = resp.get_json()
        assert len(history) >= 1
        assert history[0]["status"] == "pending"


# ─── Route registration and OpenAPI ──────────────────────────────────


class TestRouteRegistration:
    def test_parcel_detail_routes_registered(self, app):
        rules = {rule.rule for rule in app.url_map.iter_rules()}
        assert "/parcels/<int:parcel_id>" in rules
        assert "/parcels/<int:parcel_id>/destination" in rules
        assert "/parcels/<int:parcel_id>/cancel" in rules
        assert "/parcels/<int:parcel_id>/status-history" in rules

    def test_openapi_reflects_endpoints(self, client):
        resp = client.get("/openapi.json")
        spec = resp.get_json()
        assert "/parcels/{id}" in spec["paths"]
        assert "/parcels/{id}/destination" in spec["paths"]
        assert "/parcels/{id}/cancel" in spec["paths"]
