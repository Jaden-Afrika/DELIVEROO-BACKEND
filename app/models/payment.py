from datetime import datetime, timezone

from app.extensions import db
from app.models.enums import PaymentStatus


class Payment(db.Model):
    __tablename__ = "payments"

    id = db.Column(db.Integer, primary_key=True)
    parcel_id = db.Column(db.Integer, db.ForeignKey("parcels.id"), nullable=False)
    customer_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    amount = db.Column(db.Numeric(12, 2), nullable=False)
    currency = db.Column(db.String(3), nullable=False, default="KES")
    payment_method = db.Column(db.String(50), nullable=False)
    provider = db.Column(db.String(100), nullable=True)
    provider_transaction_id = db.Column(db.String(255), nullable=True, unique=True)
    payment_status = db.Column(db.Enum(PaymentStatus), nullable=False, default=PaymentStatus.pending)
    paid_at = db.Column(db.DateTime(timezone=True), nullable=True)
    created_at = db.Column(
        db.DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc)
    )
    updated_at = db.Column(
        db.DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )
