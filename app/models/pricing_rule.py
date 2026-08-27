from datetime import datetime, timezone
from app.utils import utcnow

from django.db import models

from app.models.enums import WeightCategory


class PricingRule(models.Model):
    weight_category = models.CharField(
        max_length=20, choices=[(c.value, c.name) for c in WeightCategory]
    )
    base_fee = models.DecimalField(max_digits=12, decimal_places=2)
    per_km_rate = models.DecimalField(max_digits=12, decimal_places=2)
    currency = models.CharField(max_length=3, default="KES")
    is_active = models.BooleanField(default=True)
    effective_from = models.DateTimeField()
    expires_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(default=utcnow)

    class Meta:
        app_label = "app"
        db_table = "pricing_rules"
