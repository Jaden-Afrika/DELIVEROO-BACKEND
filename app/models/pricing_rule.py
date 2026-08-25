from datetime import datetime, timezone

from app.extensions import db
from app.models.enums import WeightCategory


class PricingRule(db.Model):
    __tablename__ = "pricing_rules"

    id = db.Column(db.Integer, primary_key=True)
    weight_category = db.Column(db.Enum(WeightCategory), nullable=False)
    base_fee = db.Column(db.Numeric(12, 2), nullable=False)
    per_km_rate = db.Column(db.Numeric(12, 2), nullable=False)
    currency = db.Column(db.String(3), nullable=False, default="KES")
    is_active = db.Column(db.Boolean, nullable=False, default=True)
    effective_from = db.Column(db.DateTime(timezone=True), nullable=False)
    expires_at = db.Column(db.DateTime(timezone=True), nullable=True)
    created_at = db.Column(
        db.DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc)
    )
