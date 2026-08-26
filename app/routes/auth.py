from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token, get_jwt_identity
from marshmallow import ValidationError

from app.schemas.auth import signup_request, login_request, auth_response
from app.services.auth import create_user, authenticate_user
from app.routes.auth_decorators import auth_required

auth_bp = Blueprint("auth", __name__)


@auth_bp.route("/signup", methods=["POST"])
def signup():
    try:
        data = signup_request.load(request.get_json())
    except ValidationError as err:
        return jsonify({"error": "Validation error", "details": err.messages}), 422

    from app.extensions import db
    from app.models.user import User
    existing = User.query.filter_by(email=data["email"]).first()
    if existing:
        return jsonify({"error": "Email already registered"}), 409

    user = create_user(
        full_name=data["name"],
        email=data["email"],
        password=data["password"],
    )
    token = create_access_token(identity=str(user.id))
    return jsonify({
        "access_token": token,
        "user": user.to_dict(),
    }), 201


@auth_bp.route("/login", methods=["POST"])
def login():
    try:
        data = login_request.load(request.get_json())
    except ValidationError as err:
        return jsonify({"error": "Validation error", "details": err.messages}), 422

    user = authenticate_user(data["email"], data["password"])
    if user is None:
        return jsonify({"error": "Invalid email or password"}), 401

    token = create_access_token(identity=str(user.id))
    return jsonify({
        "access_token": token,
        "user": user.to_dict(),
    }), 200


@auth_bp.route("/logout", methods=["POST"])
@auth_required
def logout():
    return jsonify({"message": "Logged out"}), 200


@auth_bp.route("/me", methods=["GET"])
@auth_required
def me():
    from app.extensions import db
    from app.models.user import User
    user = db.session.get(User, int(get_jwt_identity()))
    return jsonify({"user": user.to_dict()}), 200
