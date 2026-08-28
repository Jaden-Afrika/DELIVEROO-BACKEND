import uuid
from datetime import datetime, timezone
from app.utils import utcnow

from django.db import models

from app.models.enums import ParcelStatus, WeightCategory


def _default_tracking_number():
    return f"DRV-{uuid.uuid4().hex[:8].upper()}"


class Parcel(models.Model):
    tracking_number = models.CharField(
        max_length=100, unique=True, db_index=True, default=_default_tracking_number
    )
    customer = models.ForeignKey(
        "app.User", on_delete=models.CASCADE, db_column="customer_id",
        related_name="parcels",
    )
    pickup_address = models.ForeignKey(
        "app.Address", on_delete=models.SET_NULL, null=True, blank=True,
        db_column="pickup_address_id", related_name="+",
    )
    destination_address = models.ForeignKey(
        "app.Address", on_delete=models.SET_NULL, null=True, blank=True,
        db_column="destination_address_id", related_name="+",
    )
    weight_category = models.CharField(
        max_length=20, choices=[(c.value, c.name) for c in WeightCategory]
    )
    weight_kg = models.DecimalField(max_digits=10, decimal_places=3, null=True, blank=True)
    description = models.TextField(null=True, blank=True)
    pickup_location = models.CharField(max_length=255)
    destination = models.CharField(max_length=255)
    distance_km = models.DecimalField(max_digits=10, decimal_places=2)
    quoted_price = models.DecimalField(max_digits=12, decimal_places=2)
    final_price = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    currency = models.CharField(max_length=3, default="KES")
    status = models.CharField(
        max_length=20,
        choices=[(s.value, s.name) for s in ParcelStatus],
        default=ParcelStatus.pending.value,
    )
    current_location = models.CharField(max_length=255, null=True, blank=True)
    created_at = models.DateTimeField(default=utcnow)
    updated_at = models.DateTimeField(default=utcnow)
    cancelled_at = models.DateTimeField(null=True, blank=True)
    delivered_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        app_label = "app"
        db_table = "parcels"
        ordering = ["-created_at"]

    def save(self, *args, **kwargs):
        self.updated_at = datetime.now(timezone.utc)
        super().save(*args, **kwargs)

    def to_dict(self):
        try:
            owner = self.customer
        except Exception:
            owner = None
        result = {
            "id": self.id,
            "trackingNumber": self.tracking_number,
            "pickupLocation": self.pickup_location,
            "destination": self.destination,
            "weightCategory": self.weight_category,
            "weight": self._weight_label(),
            "distanceKm": float(self.distance_km) if self.distance_km is not None else None,
            "estimatedTravelTime": self._estimated_travel_minutes(),
            "price": float(self.quoted_price) if self.quoted_price is not None else None,
            "currency": self.currency,
            "status": self.status,
            "currentLocation": self.current_location,
            "createdBy": str(self.customer_id),
            "ownerId": str(self.customer_id),
            "ownerName": owner.full_name if owner else None,
            "createdAt": self._iso(self.created_at),
            "dateCreated": self._iso(self.created_at),
        }
        if self.cancelled_at:
            result["cancelledAt"] = self._iso(self.cancelled_at)
        if self.delivered_at:
            result["deliveredAt"] = self._iso(self.delivered_at)
        return result

    @staticmethod
    def _iso(value):
        if not value:
            return None
        if value.tzinfo is None:
            value = value.replace(tzinfo=timezone.utc)
        return value.astimezone(timezone.utc).isoformat()

    def _estimated_travel_minutes(self):
        if self.distance_km is None:
            return None
        distance = float(self.distance_km)
        avg_speed_kmh = 40.0
        return round((distance / avg_speed_kmh) * 60)

    def _weight_label(self):
        labels = {
            WeightCategory.light.value: "Light (0 - 2kg)",
            WeightCategory.medium.value: "Medium (2 - 10kg)",
            WeightCategory.heavy.value: "Heavy (10kg+)",
        }
        return labels.get(self.weight_category, self.weight_category)
