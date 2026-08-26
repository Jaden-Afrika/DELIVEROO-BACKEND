from datetime import datetime, timezone
from flask import Blueprint, request, jsonify
from flask_jwt_extended import get_jwt_identity
from marshmallow import ValidationError

from app.extensions import db
from app.models.parcel import Parcel
from app.models.parcel_status_history import ParcelStatusHistory
from app.models.enums import ParcelStatus, WeightCategory
from app.models.user import User
from app.schemas.parcel import (
    create_parcel_request,
    update_destination_request,
)
from app.routes.auth_decorators import auth_required
from app.services.pricing import calculate_price
from app.services import get_geocoding_service, get_routing_service

parcels_bp = Blueprint("parcels", __name__)


def _get_current_user():
    user_id = int(get_jwt_identity())
    user = db.session.get(User, user_id)
    return user


def _get_parcel_or_404(parcel_id):
    parcel = db.session.get(Parcel, parcel_id)
    if parcel is None:
        return None, (jsonify({"error": {"code": "PARCEL_NOT_FOUND", "message": "Parcel not found."}}), 404)
    return parcel, None


def _check_owner_or_admin(parcel, user):
    if parcel.customer_id == user.id:
        return True
    if user.role.value == "admin":
        return True
    return False


def _record_status(parcel, status, user_id, notes=None):
    history = ParcelStatusHistory(
        parcel_id=parcel.id,
        status=status,
        changed_by_user_id=user_id,
        notes=notes,
    )
    db.session.add(history)


@parcels_bp.route("/me", methods=["GET"])
@auth_required
def list_my_parcels():
    user = _get_current_user()
    parcels = Parcel.query.filter_by(customer_id=user.id).order_by(Parcel.created_at.desc()).all()
    return jsonify([p.to_dict() for p in parcels]), 200


@parcels_bp.route("", methods=["POST"])
@auth_required
def create_parcel():
    try:
        data = create_parcel_request.load(request.get_json())
    except ValidationError as err:
        return jsonify({"error": {"code": "VALIDATION_ERROR", "message": "Validation error", "details": err.messages}}), 422

    user = _get_current_user()
    wc = WeightCategory(data["weightCategory"])
    pricing = calculate_price(wc, data["distanceKm"])

    parcel = Parcel(
        customer_id=user.id,
        weight_category=wc,
        pickup_location=data["pickupLocation"],
        destination=data["destination"],
        distance_km=data["distanceKm"],
        quoted_price=pricing["total"],
        currency=pricing["currency"],
        description=data.get("description"),
    )
    db.session.add(parcel)
    db.session.flush()

    _record_status(parcel, ParcelStatus.pending, user.id, notes="Parcel created")
    db.session.commit()

    return jsonify(parcel.to_dict()), 201


@parcels_bp.route("/<int:parcel_id>", methods=["GET"])
@auth_required
def get_parcel(parcel_id):
    user = _get_current_user()
    parcel, error = _get_parcel_or_404(parcel_id)
    if error:
        return error

    if not _check_owner_or_admin(parcel, user):
        return jsonify({"error": {"code": "PARCEL_NOT_FOUND", "message": "Parcel not found."}}), 404

    return jsonify(parcel.to_dict()), 200


@parcels_bp.route("/<int:parcel_id>/destination", methods=["PATCH"])
@auth_required
def update_destination(parcel_id):
    user = _get_current_user()
    parcel, error = _get_parcel_or_404(parcel_id)
    if error:
        return error

    if not _check_owner_or_admin(parcel, user):
        return jsonify({"error": {"code": "PARCEL_NOT_FOUND", "message": "Parcel not found."}}), 404

    if parcel.status == ParcelStatus.delivered:
        return jsonify({"error": {"code": "PARCEL_DELIVERED", "message": "Cannot update destination for a delivered parcel."}}), 409
    if parcel.status == ParcelStatus.cancelled:
        return jsonify({"error": {"code": "PARCEL_CANCELLED", "message": "Cannot update destination for a cancelled parcel."}}), 409

    try:
        data = update_destination_request.load(request.get_json())
    except ValidationError as err:
        return jsonify({"error": {"code": "VALIDATION_ERROR", "message": "Validation error", "details": err.messages}}), 422

    new_destination = data["destination"]
    if new_destination.strip() == parcel.destination.strip():
        return jsonify(parcel.to_dict()), 200

    try:
        geocoder = get_geocoding_service()
        router = get_routing_service()

        pickup_geo = geocoder.geocode(parcel.pickup_location)
        dest_geo = geocoder.geocode(new_destination)

        if pickup_geo and dest_geo:
            route = router.get_route(
                pickup_geo.latitude, pickup_geo.longitude,
                dest_geo.latitude, dest_geo.longitude,
            )
            if route:
                parcel.distance_km = route.distance_km
                pricing = calculate_price(parcel.weight_category, route.distance_km)
                parcel.quoted_price = pricing["total"]
                parcel.currency = pricing["currency"]

        parcel.destination = new_destination
        if dest_geo:
            parcel.current_location = dest_geo.formatted_address

        _record_status(parcel, parcel.status, user.id, notes=f"Destination changed to: {new_destination}")
        db.session.commit()
    except Exception:
        db.session.rollback()
        return jsonify({"error": {"code": "UPDATE_FAILED", "message": "Failed to update destination."}}), 500

    return jsonify(parcel.to_dict()), 200


@parcels_bp.route("/<int:parcel_id>/cancel", methods=["PATCH"])
@auth_required
def cancel_parcel(parcel_id):
    user = _get_current_user()
    parcel, error = _get_parcel_or_404(parcel_id)
    if error:
        return error

    if not _check_owner_or_admin(parcel, user):
        return jsonify({"error": {"code": "PARCEL_NOT_FOUND", "message": "Parcel not found."}}), 404

    if parcel.status == ParcelStatus.delivered:
        return jsonify({"error": {"code": "PARCEL_DELIVERED", "message": "Cannot cancel a delivered parcel."}}), 409
    if parcel.status == ParcelStatus.cancelled:
        return jsonify({"error": {"code": "PARCEL_CANCELLED", "message": "Parcel is already cancelled."}}), 409

    try:
        parcel.status = ParcelStatus.cancelled
        parcel.cancelled_at = datetime.now(timezone.utc)
        _record_status(parcel, ParcelStatus.cancelled, user.id, notes="Parcel cancelled by owner")
        db.session.commit()
    except Exception:
        db.session.rollback()
        return jsonify({"error": {"code": "CANCEL_FAILED", "message": "Failed to cancel parcel."}}), 500

    return jsonify(parcel.to_dict()), 200


@parcels_bp.route("/<int:parcel_id>/status-history", methods=["GET"])
@auth_required
def get_status_history(parcel_id):
    user = _get_current_user()
    parcel, error = _get_parcel_or_404(parcel_id)
    if error:
        return error

    if not _check_owner_or_admin(parcel, user):
        return jsonify({"error": {"code": "PARCEL_NOT_FOUND", "message": "Parcel not found."}}), 404

    history = (
        ParcelStatusHistory.query
        .filter_by(parcel_id=parcel.id)
        .order_by(ParcelStatusHistory.created_at.asc())
        .all()
    )
    return jsonify([
        {
            "id": h.id,
            "status": h.status.value,
            "changedByUserId": h.changed_by_user_id,
            "notes": h.notes,
            "createdAt": h.created_at.isoformat() if h.created_at else None,
        }
        for h in history
    ]), 200


@parcels_bp.route("/<int:parcel_id>/tracking", methods=["GET"])
@auth_required
def get_tracking(parcel_id):
    user = _get_current_user()
    parcel, error = _get_parcel_or_404(parcel_id)
    if error:
        return error

    if not _check_owner_or_admin(parcel, user):
        return jsonify({"error": {"code": "PARCEL_NOT_FOUND", "message": "Parcel not found."}}), 404

    return jsonify({"message": "Not implemented", "locations": []}), 501
