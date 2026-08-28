import pytest
from datetime import datetime, timezone

from rest_framework.test import APIClient

from app.models.pricing_rule import PricingRule
from app.models.enums import WeightCategory, UserRole
from app.services.auth import create_user


@pytest.fixture
def client(db):
    return APIClient()


@pytest.fixture
def seed_pricing_rules(db):
    now = datetime.now(timezone.utc)
    rules = [
        PricingRule(weight_category=WeightCategory.light.value, base_fee=150, per_km_rate=15, currency="KES", is_active=True, effective_from=now),
        PricingRule(weight_category=WeightCategory.medium.value, base_fee=350, per_km_rate=25, currency="KES", is_active=True, effective_from=now),
        PricingRule(weight_category=WeightCategory.heavy.value, base_fee=700, per_km_rate=40, currency="KES", is_active=True, effective_from=now),
    ]
    PricingRule.objects.bulk_create(rules)
    return rules


@pytest.fixture
def seed_users(db):
    user = create_user(full_name="Test User", email="test@example.com", password="password123", role=UserRole.user.value)
    admin = create_user(full_name="Test Admin", email="admin@example.com", password="password123", role=UserRole.admin.value)
    other = create_user(full_name="Other User", email="other@example.com", password="password123", role=UserRole.user.value)
    return {"user": user, "admin": admin, "other": other}


def _login_token(client, email, password):
    resp = client.post("/auth/login", {"email": email, "password": password}, format="json")
    assert resp.status_code == 200, resp.content
    return resp.data["access_token"]


@pytest.fixture
def user_token(client, seed_users):
    return _login_token(client, "test@example.com", "password123")


@pytest.fixture
def admin_token(client, seed_users):
    return _login_token(client, "admin@example.com", "password123")


@pytest.fixture
def other_token(client, seed_users):
    return _login_token(client, "other@example.com", "password123")


@pytest.fixture
def auth_header(user_token):
    return {"HTTP_AUTHORIZATION": f"Bearer {user_token}"}


@pytest.fixture
def admin_header(admin_token):
    return {"HTTP_AUTHORIZATION": f"Bearer {admin_token}"}


@pytest.fixture
def other_header(other_token):
    return {"HTTP_AUTHORIZATION": f"Bearer {other_token}"}
