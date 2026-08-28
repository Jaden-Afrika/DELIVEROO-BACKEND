from datetime import datetime, timezone
from app.utils import utcnow

from django.db import models

from app.models.enums import DriverAvailabilityStatus


class Driver(models.Model):
    user = models.OneToOneField(
        "app.User", on_delete=models.CASCADE, db_column="user_id", related_name="driver_profile"
    )
    vehicle_type = models.CharField(max_length=100)
    vehicle_registration = models.CharField(max_length=100)
    licence_number = models.CharField(max_length=100)
    availability_status = models.CharField(
        max_length=20,
        choices=[(s.value, s.name) for s in DriverAvailabilityStatus],
        default=DriverAvailabilityStatus.offline.value,
    )
    is_verified = models.BooleanField(default=False)
    created_at = models.DateTimeField(default=utcnow)
    updated_at = models.DateTimeField(default=utcnow)

    class Meta:
        app_label = "app"
        db_table = "drivers"
