from datetime import datetime, timezone
from app.utils import utcnow

from django.db import models


class TrackingLocation(models.Model):
    delivery = models.ForeignKey(
        "app.Delivery", on_delete=models.CASCADE, db_column="delivery_id", related_name="tracking_locations"
    )
    latitude = models.DecimalField(max_digits=9, decimal_places=6)
    longitude = models.DecimalField(max_digits=9, decimal_places=6)
    location_text = models.CharField(max_length=255, null=True, blank=True)
    recorded_at = models.DateTimeField(default=utcnow)

    class Meta:
        app_label = "app"
        db_table = "tracking_locations"
