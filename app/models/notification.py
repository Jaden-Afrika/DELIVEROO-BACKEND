from datetime import datetime, timezone
from app.utils import utcnow

from django.db import models


class Notification(models.Model):
    user = models.ForeignKey(
        "app.User", on_delete=models.CASCADE, db_column="user_id", related_name="notifications"
    )
    parcel = models.ForeignKey(
        "app.Parcel", on_delete=models.CASCADE, null=True, blank=True,
        db_column="parcel_id", related_name="notifications",
    )
    type = models.CharField(max_length=100)
    title = models.CharField(max_length=255)
    message = models.TextField()
    read_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(default=utcnow)

    class Meta:
        app_label = "app"
        db_table = "notifications"
