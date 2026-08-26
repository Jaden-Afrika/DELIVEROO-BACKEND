import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pytest
from app import create_app
from app.config import TestConfig
from app.extensions import db as _db


@pytest.fixture(scope="function")
def app():
    app = create_app(TestConfig)
    with app.app_context():
        _db.create_all()
        yield app
        _db.session.remove()
        _db.drop_all()


@pytest.fixture(scope="function")
def client(app):
    return app.test_client()


@pytest.fixture(scope="function")
def db_session(app):
    with app.app_context():
        yield _db.session
        _db.session.remove()


@pytest.fixture
def seed_pricing_rules(db_session):
    from datetime import datetime, timezone
    from app.models.pricing_rule import PricingRule
    from app.models.enums import WeightCategory

    now = datetime.now(timezone.utc)
    rules = [
        PricingRule(weight_category=WeightCategory.light, base_fee=150, per_km_rate=15, currency="KES", is_active=True, effective_from=now),
        PricingRule(weight_category=WeightCategory.medium, base_fee=350, per_km_rate=25, currency="KES", is_active=True, effective_from=now),
        PricingRule(weight_category=WeightCategory.heavy, base_fee=700, per_km_rate=40, currency="KES", is_active=True, effective_from=now),
    ]
    db_session.add_all(rules)
    db_session.commit()
    return rules


@pytest.fixture
def seed_users(db_session):
    from app.services.auth import create_user
    from app.models.enums import UserRole

    user = create_user(full_name="Test User", email="test@example.com", password="password123", role=UserRole.user)
    admin = create_user(full_name="Test Admin", email="admin@example.com", password="password123", role=UserRole.admin)
    other = create_user(full_name="Other User", email="other@example.com", password="password123", role=UserRole.user)
    return {"user": user, "admin": admin, "other": other}


@pytest.fixture
def other_token(client, seed_users):
    resp = client.post("/auth/login", json={"email": "other@example.com", "password": "password123"})
    return resp.get_json()["access_token"]


@pytest.fixture
def other_header(other_token):
    return {"Authorization": f"Bearer {other_token}"}


@pytest.fixture
def user_token(client, seed_users):
    resp = client.post("/auth/login", json={"email": "test@example.com", "password": "password123"})
    return resp.get_json()["access_token"]


@pytest.fixture
def admin_token(client, seed_users):
    resp = client.post("/auth/login", json={"email": "admin@example.com", "password": "password123"})
    return resp.get_json()["access_token"]


@pytest.fixture
def auth_header(user_token):
    return {"Authorization": f"Bearer {user_token}"}


@pytest.fixture
def admin_header(admin_token):
    return {"Authorization": f"Bearer {admin_token}"}
