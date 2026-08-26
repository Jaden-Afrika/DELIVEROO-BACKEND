import uuid
from datetime import datetime, timezone

from app.extensions import db
from app.models.enums import ParcelStatus, WeightCategory


class Parcel(db.Model):
    __tablename__ = "parcels"

    id = db.Column(db.Integer, primary_key=True)
    tracking_number = db.Column(
        db.String(100), nullable=False, unique=True, index=True,
        default=lambda: f"DRV-{uuid.uuid4().hex[:8].upper()}"
    )
    customer_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    pickup_address_id = db.Column(db.Integer, db.ForeignKey("addresses.id"), nullable=True)
    destination_address_id = db.Column(db.Integer, db.ForeignKey("addresses.id"), nullable=True)
    weight_category = db.Column(db.Enum(WeightCategory), nullable=False)
    weight_kg = db.Column(db.Numeric(10, 3), nullable=True)
    description = db.Column(db.Text, nullable=True)
    pickup_location = db.Column(db.String(255), nullable=False)
    destination = db.Column(db.String(255), nullable=False)
    distance_km = db.Column(db.Numeric(10, 2), nullable=False)
    quoted_price = db.Column(db.Numeric(12, 2), nullable=False)
    final_price = db.Column(db.Numeric(12, 2), nullable=True)
    currency = db.Column(db.String(3), nullable=False, default="KES")
    status = db.Column(db.Enum(ParcelStatus), nullable=False, default=ParcelStatus.pending)
    current_location = db.Column(db.String(255), nullable=True)
    created_at = db.Column(
        db.DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc)
    )
    updated_at = db.Column(
        db.DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )
    cancelled_at = db.Column(db.DateTime(timezone=True), nullable=True)
    delivered_at = db.Column(db.DateTime(timezone=True), nullable=True)

    pickup_address = db.relationship("Address", foreign_keys=[pickup_address_id], lazy=True)
    destination_address = db.relationship("Address", foreign_keys=[destination_address_id], lazy=True)
    status_history = db.relationship("ParcelStatusHistory", backref="parcel", lazy=True)
    delivery = db.relationship("Delivery", backref="parcel", uselist=False, lazy=True)
    payments = db.relationship("Payment", backref="parcel", lazy=True)

    def to_dict(self):
        owner = self.customer
        result = {
            "id": self.id,
            "trackingNumber": self.tracking_number,
            "pickupLocation": self.pickup_location,
            "destination": self.destination,
            "weightCategory": self.weight_category.value,
            "weight": self._weight_label(),
            "distanceKm": float(self.distance_km) if self.distance_km else None,
            "estimatedTravelTime": self._estimated_travel_minutes(),
            "price": float(self.quoted_price) if self.quoted_price else None,
            "currency": self.currency,
            "status": self.status.value,
            "currentLocation": self.current_location,
            "createdBy": str(self.customer_id),
            "ownerId": str(self.customer_id),
            "ownerName": owner.full_name if owner else None,
            "createdAt": self.created_at.isoformat() if self.created_at else None,
            "dateCreated": self.created_at.isoformat() if self.created_at else None,
        }
        if self.cancelled_at:
            result["cancelledAt"] = self.cancelled_at.isoformat()
        if self.delivered_at:
            result["deliveredAt"] = self.delivered_at.isoformat()
        return result

    def _estimated_travel_minutes(self):
        if self.distance_km is None:
            return None
        distance = float(self.distance_km)
        avg_speed_kmh = 40.0
        minutes = (distance / avg_speed_kmh) * 60
        return round(minutes)

    def _weight_label(self):
        labels = {
            WeightCategory.light: "Light (0 - 2kg)",
            WeightCategory.medium: "Medium (2 - 10kg)",
            WeightCategory.heavy: "Heavy (10kg+)",
        }
        return labels.get(self.weight_category, self.weight_category.value)
