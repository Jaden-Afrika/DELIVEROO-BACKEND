from datetime import datetime, timezone
from app.utils import utcnow

from django.db import models

from app.models.enums import PaymentStatus


class Payment(models.Model):
    parcel = models.ForeignKey(
        "app.Parcel", on_delete=models.CASCADE, db_column="parcel_id", related_name="payments"
    )
    customer = models.ForeignKey(
        "app.User", on_delete=models.CASCADE, db_column="customer_id", related_name="payments"
    )
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    currency = models.CharField(max_length=3, default="KES")
    payment_method = models.CharField(max_length=50)
    provider = models.CharField(max_length=100, null=True, blank=True)
    provider_transaction_id = models.CharField(max_length=255, unique=True, null=True, blank=True)
    payment_status = models.CharField(
        max_length=20,
        choices=[(s.value, s.name) for s in PaymentStatus],
        default=PaymentStatus.pending.value,
    )
    paid_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(default=utcnow)
    updated_at = models.DateTimeField(default=utcnow)

    class Meta:
        app_label = "app"
        db_table = "payments"
