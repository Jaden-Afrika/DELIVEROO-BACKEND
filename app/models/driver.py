from datetime import datetime, timezone

from app.extensions import db
from app.models.enums import DriverAvailabilityStatus


class Driver(db.Model):
    __tablename__ = "drivers"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False, unique=True)
    vehicle_type = db.Column(db.String(100), nullable=False)
    vehicle_registration = db.Column(db.String(100), nullable=False)
    licence_number = db.Column(db.String(100), nullable=False)
    availability_status = db.Column(
        db.Enum(DriverAvailabilityStatus),
        nullable=False,
        default=DriverAvailabilityStatus.offline,
    )
    is_verified = db.Column(db.Boolean, nullable=False, default=False)
    created_at = db.Column(
        db.DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc)
    )
    updated_at = db.Column(
        db.DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    deliveries = db.relationship("Delivery", backref="driver", lazy=True)
