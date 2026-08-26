from flask import Blueprint, request, jsonify
from marshmallow import ValidationError
from flask_jwt_extended import get_jwt_identity

from app.extensions import db
from app.models.parcel import Parcel
from app.models.parcel_status_history import ParcelStatusHistory
from app.models.enums import ParcelStatus
from app.models.user import User
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
    parcel = db.session.get(Parcel, parcel_id)
    if parcel is None:
        return jsonify({"error": {"code": "PARCEL_NOT_FOUND", "message": "Parcel not found."}}), 404

    try:
        data = admin_update_status_request.load(request.get_json())
    except ValidationError as err:
        return jsonify({"error": {"code": "VALIDATION_ERROR", "message": "Validation error", "details": err.messages}}), 422

    user_id = int(get_jwt_identity())
    new_status = ParcelStatus(data["status"])

    if parcel.status == new_status:
        return jsonify(parcel.to_dict()), 200

    parcel.status = new_status
    history = ParcelStatusHistory(
        parcel_id=parcel.id,
        status=new_status,
        changed_by_user_id=user_id,
        notes=f"Status changed to {new_status.value} by admin",
    )
    db.session.add(history)
    db.session.commit()
    return jsonify(parcel.to_dict()), 200


@admin_bp.route("/parcels/<int:parcel_id>/location", methods=["PATCH"])
@admin_required
def update_parcel_location(parcel_id):
    parcel = db.session.get(Parcel, parcel_id)
    if parcel is None:
        return jsonify({"error": {"code": "PARCEL_NOT_FOUND", "message": "Parcel not found."}}), 404

    try:
        data = admin_update_location_request.load(request.get_json())
    except ValidationError as err:
        return jsonify({"error": {"code": "VALIDATION_ERROR", "message": "Validation error", "details": err.messages}}), 422

    parcel.current_location = data["currentLocation"]
    db.session.commit()
    return jsonify(parcel.to_dict()), 200
