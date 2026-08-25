from datetime import datetime, timezone

from app.extensions import db


class TrackingLocation(db.Model):
    __tablename__ = "tracking_locations"

    id = db.Column(db.Integer, primary_key=True)
    delivery_id = db.Column(db.Integer, db.ForeignKey("deliveries.id"), nullable=False)
    latitude = db.Column(db.Numeric(9, 6), nullable=False)
    longitude = db.Column(db.Numeric(9, 6), nullable=False)
    location_text = db.Column(db.String(255), nullable=True)
    recorded_at = db.Column(
        db.DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc)
    )
