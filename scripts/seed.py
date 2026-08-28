"""Idempotent seed script. Run with: python -m scripts.seed"""

import os

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")

import django

django.setup()

from datetime import datetime, timezone

from app.models.user import User
from app.models.pricing_rule import PricingRule
from app.models.enums import UserRole, WeightCategory
from app.services.auth import create_user


def seed():
    now = datetime.now(timezone.utc)

    # Seed pricing rules
    existing_rules = PricingRule.objects.count()
    if existing_rules == 0:
        rules = [
            PricingRule(
                weight_category=WeightCategory.light.value,
                base_fee=150,
                per_km_rate=15,
                currency="KES",
                is_active=True,
                effective_from=now,
            ),
            PricingRule(
                weight_category=WeightCategory.medium.value,
                base_fee=350,
                per_km_rate=25,
                currency="KES",
                is_active=True,
                effective_from=now,
            ),
            PricingRule(
                weight_category=WeightCategory.heavy.value,
                base_fee=700,
                per_km_rate=40,
                currency="KES",
                is_active=True,
                effective_from=now,
            ),
        ]
        PricingRule.objects.bulk_create(rules)
        print(f"Seeded {len(rules)} pricing rules")
    else:
        print(f"Pricing rules already exist ({existing_rules} found), skipping")

    # Seed dev users
    dev_user = User.objects.filter(email="user@deliveroo.dev").first()
    if dev_user is None:
        user = create_user(
            full_name="Dev User",
            email="user@deliveroo.dev",
            password="password123",
            role=UserRole.user.value,
        )
        print(f"Created dev user: {user.email} (id={user.id})")
    else:
        print(f"Dev user already exists (id={dev_user.id}), skipping")

    dev_admin = User.objects.filter(email="admin@deliveroo.dev").first()
    if dev_admin is None:
        admin = create_user(
            full_name="Dev Admin",
            email="admin@deliveroo.dev",
            password="password123",
            role=UserRole.admin.value,
        )
        print(f"Created dev admin: {admin.email} (id={admin.id})")
    else:
        print(f"Dev admin already exists (id={dev_admin.id}), skipping")

    print("Seed complete.")


if __name__ == "__main__":
    seed()
