from datetime import datetime, timezone
from app.utils import utcnow

from django.db import models

from app.models.enums import ParcelStatus


class ParcelStatusHistory(models.Model):
    parcel = models.ForeignKey(
        "app.Parcel", on_delete=models.CASCADE, db_column="parcel_id",
        related_name="status_history",
    )
    status = models.CharField(
        max_length=20, choices=[(s.value, s.name) for s in ParcelStatus]
    )
    changed_by_user = models.ForeignKey(
        "app.User", on_delete=models.SET_NULL, null=True, blank=True,
        db_column="changed_by_user_id", related_name="+",
    )
    notes = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(default=utcnow)

    class Meta:
        app_label = "app"
        db_table = "parcel_status_history"
        ordering = ["created_at"]
