from datetime import datetime, timezone
from app.utils import utcnow

from django.db import models


class Address(models.Model):
    user = models.ForeignKey(
        "app.User", on_delete=models.CASCADE, db_column="user_id", related_name="addresses"
    )
    label = models.CharField(max_length=100, null=True, blank=True)
    recipient_name = models.CharField(max_length=255)
    recipient_phone = models.CharField(max_length=50)
    address_line_1 = models.CharField(max_length=255)
    address_line_2 = models.CharField(max_length=255, null=True, blank=True)
    city = models.CharField(max_length=100)
    region_or_state = models.CharField(max_length=100)
    country = models.CharField(max_length=100)
    postal_code = models.CharField(max_length=20, null=True, blank=True)
    latitude = models.DecimalField(max_digits=9, decimal_places=6)
    longitude = models.DecimalField(max_digits=9, decimal_places=6)
    created_at = models.DateTimeField(default=utcnow)
    updated_at = models.DateTimeField(default=utcnow)

    class Meta:
        app_label = "app"
        db_table = "addresses"
