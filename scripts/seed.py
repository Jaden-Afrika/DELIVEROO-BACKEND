"""Idempotent seed script. Run with: python -m scripts.seed"""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from datetime import datetime, timezone
from app import create_app
from app.extensions import db
from app.models.user import User
from app.models.enums import UserRole, WeightCategory
from app.models.pricing_rule import PricingRule
from app.services.auth import create_user


def seed():
    app = create_app()
    with app.app_context():
        db.create_all()

        # Seed pricing rules
        now = datetime.now(timezone.utc)
        existing_rules = PricingRule.query.count()
        if existing_rules == 0:
            rules = [
                PricingRule(
                    weight_category=WeightCategory.light,
                    base_fee=150,
                    per_km_rate=15,
                    currency="KES",
                    is_active=True,
                    effective_from=now,
                ),
                PricingRule(
                    weight_category=WeightCategory.medium,
                    base_fee=350,
                    per_km_rate=25,
                    currency="KES",
                    is_active=True,
                    effective_from=now,
                ),
                PricingRule(
                    weight_category=WeightCategory.heavy,
                    base_fee=700,
                    per_km_rate=40,
                    currency="KES",
                    is_active=True,
                    effective_from=now,
                ),
            ]
            db.session.add_all(rules)
            db.session.commit()
            print(f"Seeded {len(rules)} pricing rules")
        else:
            print(f"Pricing rules already exist ({existing_rules} found), skipping")

        # Seed dev users
        dev_user = User.query.filter_by(email="user@deliveroo.dev").first()
        if dev_user is None:
            user = create_user(
                full_name="Dev User",
                email="user@deliveroo.dev",
                password="password123",
                role=UserRole.user,
            )
            print(f"Created dev user: {user.email} (id={user.id})")
        else:
            print(f"Dev user already exists (id={dev_user.id}), skipping")

        dev_admin = User.query.filter_by(email="admin@deliveroo.dev").first()
        if dev_admin is None:
            admin = create_user(
                full_name="Dev Admin",
                email="admin@deliveroo.dev",
                password="password123",
                role=UserRole.admin,
            )
            print(f"Created dev admin: {admin.email} (id={admin.id})")
        else:
            print(f"Dev admin already exists (id={dev_admin.id}), skipping")

        print("Seed complete.")


if __name__ == "__main__":
    seed()
