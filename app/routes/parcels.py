from flask import Blueprint, request, jsonify, abort
from flask_jwt_extended import get_jwt_identity
from marshmallow import ValidationError

from app.extensions import db
from app.models.parcel import Parcel
from app.models.enums import ParcelStatus, WeightCategory
from app.schemas.parcel import (
    create_parcel_request,
    update_destination_request,
)
from app.routes.auth_decorators import auth_required
from app.services.pricing import calculate_price

parcels_bp = Blueprint("parcels", __name__)


def _get_own_parcel_or_404(parcel_id):
    """Look up a parcel, but only if it belongs to the current user.
    Returns 404 (not 403) for someone else's parcel, matching the
    existing test's expectation and avoiding leaking that the id exists."""
    user_id = int(get_jwt_identity())
    parcel = Parcel.query.filter_by(id=parcel_id, customer_id=user_id).first()
    if parcel is None:
        abort(404)
    return parcel


def _require_not_delivered(parcel):
    """Cancel/change-destination are only allowed before a parcel is
    delivered — enforced here, not just in the frontend UI."""
    if parcel.status == ParcelStatus.delivered:
        abort(409, description="Cannot modify a parcel that has already been delivered.")


@parcels_bp.route("/me", methods=["GET"])
@auth_required
def list_my_parcels():
    user_id = int(get_jwt_identity())
    parcels = Parcel.query.filter_by(customer_id=user_id).order_by(Parcel.created_at.desc()).all()
    return jsonify([p.to_dict() for p in parcels]), 200


@parcels_bp.route("", methods=["POST"])
@auth_required
def create_parcel():
    try:
        data = create_parcel_request.load(request.get_json())
    except ValidationError as err:
        return jsonify({"error": err.messages}), 422

    user_id = int(get_jwt_identity())
    wc = WeightCategory(data["weightCategory"])
    pricing = calculate_price(wc, data["distanceKm"])

    parcel = Parcel(
        customer_id=user_id,
        weight_category=wc,
        pickup_location=data["pickupLocation"],
        destination=data["destination"],
        distance_km=data["distanceKm"],
        quoted_price=pricing["total"],
        currency=pricing["currency"],
        description=data.get("description"),
    )
    db.session.add(parcel)
    db.session.commit()

    return jsonify(parcel.to_dict()), 201


@parcels_bp.route("/<int:parcel_id>", methods=["GET"])
@auth_required
def get_parcel(parcel_id):
    parcel = _get_own_parcel_or_404(parcel_id)
    return jsonify(parcel.to_dict()), 200


@parcels_bp.route("/<int:parcel_id>/destination", methods=["PATCH"])
@auth_required
def update_destination(parcel_id):
    parcel = _get_own_parcel_or_404(parcel_id)
    _require_not_delivered(parcel)

    try:
        data = update_destination_request.load(request.get_json())
    except ValidationError as err:
        return jsonify({"error": err.messages}), 422

    parcel.destination = data["destination"]
    db.session.commit()

    return jsonify(parcel.to_dict()), 200


@parcels_bp.route("/<int:parcel_id>/cancel", methods=["PATCH"])
@auth_required
def cancel_parcel(parcel_id):
    parcel = _get_own_parcel_or_404(parcel_id)
    _require_not_delivered(parcel)

    parcel.status = ParcelStatus.cancelled
    db.session.commit()

    return jsonify(parcel.to_dict()), 200


@parcels_bp.route("/<int:parcel_id>/status-history", methods=["GET"])
@auth_required
def get_status_history(parcel_id):
    return jsonify({"message": "Not implemented"}), 501


@parcels_bp.route("/<int:parcel_id>/tracking", methods=["GET"])
@auth_required
def get_tracking(parcel_id):
    return jsonify({"message": "Not implemented"}), 501
