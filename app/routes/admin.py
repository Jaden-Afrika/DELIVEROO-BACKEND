from flask import Blueprint, request, jsonify
from marshmallow import ValidationError

from app.extensions import db
from app.models.parcel import Parcel
from app.models.enums import ParcelStatus
from app.schemas.parcel import (
    admin_update_status_request,
    admin_update_location_request,
)
from app.routes.auth_decorators import admin_required

admin_bp = Blueprint("admin", __name__)


@admin_bp.route("/parcels", methods=["GET"])
@admin_required
def list_all_parcels():
    parcels = Parcel.query.order_by(Parcel.created_at.desc()).all()
    return jsonify([p.to_dict() for p in parcels]), 200


@admin_bp.route("/parcels/<int:parcel_id>/status", methods=["PATCH"])
@admin_required
def update_parcel_status(parcel_id):
    parcel = Parcel.query.get_or_404(parcel_id)
    try:
        data = admin_update_status_request.load(request.get_json())
    except ValidationError as err:
        return jsonify({"error": err.messages}), 422

    new_status = ParcelStatus(data["status"])
    parcel.status = new_status
    db.session.commit()

    return jsonify(parcel.to_dict()), 200


@admin_bp.route("/parcels/<int:parcel_id>/location", methods=["PATCH"])
@admin_required
def update_parcel_location(parcel_id):
    parcel = Parcel.query.get_or_404(parcel_id)
    try:
        data = admin_update_location_request.load(request.get_json())
    except ValidationError as err:
        return jsonify({"error": err.messages}), 422

    parcel.current_location = data["currentLocation"]
    db.session.commit()

    return jsonify(parcel.to_dict()), 200
