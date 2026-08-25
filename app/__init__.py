import os
from flask import Flask, jsonify
from dotenv import load_dotenv

load_dotenv()

from app.extensions import db, migrate, jwt, cors
from app.config import Config
from app.errors import register_error_handlers
from app.models import *  # noqa: F401, F403 — ensure all models are imported for migrations


def create_app(config_class=None):
    app = Flask(__name__)
    app.config.from_object(config_class or Config)

    db.init_app(app)
    migrate.init_app(app, db)
    jwt.init_app(app)
    cors.init_app(app, resources={r"/*": {"origins": app.config.get("FRONTEND_ORIGIN", "*")}})

    register_error_handlers(app)

    from app.routes.auth import auth_bp
    from app.routes.parcels import parcels_bp
    from app.routes.admin import admin_bp

    prefix = app.config.get("API_PREFIX", "")
    app.register_blueprint(auth_bp, url_prefix=f"{prefix}/auth")
    app.register_blueprint(parcels_bp, url_prefix=f"{prefix}/parcels")
    app.register_blueprint(admin_bp, url_prefix=f"{prefix}/admin")

    @app.get("/")
    def health_check():
        return {"status": "ok", "service": "deliveroo-backend"}

    @app.get("/health")
    def health():
        return {"status": "ok", "service": "deliveroo-backend"}

    @app.get("/openapi.json")
    def openapi():
        return jsonify(_build_openapi_spec(app))

    return app


def _build_openapi_spec(app):
    return {
        "openapi": "3.0.3",
        "info": {
            "title": "Deliveroo Backend API",
            "version": "0.1.0",
            "description": "Courier parcel delivery API",
        },
        "paths": {
            "/auth/signup": {"post": {"summary": "Register a new user", "tags": ["auth"]}},
            "/auth/login": {"post": {"summary": "Log in", "tags": ["auth"]}},
            "/auth/logout": {"post": {"summary": "Log out", "tags": ["auth"]}},
            "/auth/me": {"get": {"summary": "Current user", "tags": ["auth"]}},
            "/parcels/me": {"get": {"summary": "List my parcels", "tags": ["parcels"]}},
            "/parcels": {
                "post": {"summary": "Create parcel", "tags": ["parcels"]},
                "get": {"summary": "List parcels", "tags": ["parcels"]},
            },
            "/parcels/{id}": {"get": {"summary": "Get parcel", "tags": ["parcels"]}},
            "/parcels/{id}/destination": {"patch": {"summary": "Update destination", "tags": ["parcels"]}},
            "/parcels/{id}/cancel": {"patch": {"summary": "Cancel parcel", "tags": ["parcels"]}},
            "/parcels/{id}/status-history": {"get": {"summary": "Status history", "tags": ["parcels"]}},
            "/parcels/{id}/tracking": {"get": {"summary": "Tracking", "tags": ["parcels"]}},
            "/admin/parcels": {"get": {"summary": "List all parcels (admin)", "tags": ["admin"]}},
            "/admin/parcels/{id}/status": {"patch": {"summary": "Update status (admin)", "tags": ["admin"]}},
            "/admin/parcels/{id}/location": {"patch": {"summary": "Update location (admin)", "tags": ["admin"]}},
        },
    }
