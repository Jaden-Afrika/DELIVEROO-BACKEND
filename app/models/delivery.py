from datetime import datetime, timezone
from app.utils import utcnow

from django.db import models


class Delivery(models.Model):
    parcel = models.OneToOneField(
        "app.Parcel", on_delete=models.CASCADE, db_column="parcel_id", related_name="delivery"
    )
    driver = models.ForeignKey(
        "app.Driver", on_delete=models.SET_NULL, null=True, blank=True,
        db_column="driver_id", related_name="deliveries",
    )
    assigned_by_user = models.ForeignKey(
        "app.User", on_delete=models.SET_NULL, null=True, blank=True,
        db_column="assigned_by_user_id", related_name="+",
    )
    assigned_at = models.DateTimeField(null=True, blank=True)
    picked_up_at = models.DateTimeField(null=True, blank=True)
    delivered_at = models.DateTimeField(null=True, blank=True)
    delivery_notes = models.TextField(null=True, blank=True)
    proof_of_delivery_url = models.CharField(max_length=1000, null=True, blank=True)
    created_at = models.DateTimeField(default=utcnow)
    updated_at = models.DateTimeField(default=utcnow)

    class Meta:
        app_label = "app"
        db_table = "deliveries"
