from datetime import datetime, timezone

from app.extensions import db


class Delivery(db.Model):
    __tablename__ = "deliveries"

    id = db.Column(db.Integer, primary_key=True)
    parcel_id = db.Column(db.Integer, db.ForeignKey("parcels.id"), nullable=False, unique=True)
    driver_id = db.Column(db.Integer, db.ForeignKey("drivers.id"), nullable=True)
    assigned_by_user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=True)
    assigned_at = db.Column(db.DateTime(timezone=True), nullable=True)
    picked_up_at = db.Column(db.DateTime(timezone=True), nullable=True)
    delivered_at = db.Column(db.DateTime(timezone=True), nullable=True)
    delivery_notes = db.Column(db.Text, nullable=True)
    proof_of_delivery_url = db.Column(db.String(1000), nullable=True)
    created_at = db.Column(
        db.DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc)
    )
    updated_at = db.Column(
        db.DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    tracking_locations = db.relationship("TrackingLocation", backref="delivery", lazy=True)
