from app.models import (
    User, Driver, Address, PricingRule, Parcel,
    ParcelStatusHistory, Delivery, TrackingLocation,
    Payment, Notification,
)
from app.models.enums import (
    UserRole, DriverAvailabilityStatus, ParcelStatus,
    WeightCategory, PaymentStatus,
)


def test_user_model_fields():
    cols = {c.name for c in User.__table__.columns}
    assert "id" in cols
    assert "full_name" in cols
    assert "email" in cols
    assert "password_hash" in cols
    assert "role" in cols
    assert "is_active" in cols
    assert "created_at" in cols
    assert "updated_at" in cols


def test_user_to_dict():
    from app.extensions import db
    from datetime import datetime, timezone
    user = User(id=1, full_name="Test", email="t@t.com", role=UserRole.user, is_active=True,
                created_at=datetime.now(timezone.utc), updated_at=datetime.now(timezone.utc))
    d = user.to_dict()
    assert d["name"] == "Test"
    assert d["role"] == "user"
    assert "id" in d
    assert "email" in d


def test_parcel_model_fields():
    cols = {c.name for c in Parcel.__table__.columns}
    assert "tracking_number" in cols
    assert "customer_id" in cols
    assert "pickup_location" in cols
    assert "destination" in cols
    assert "weight_category" in cols
    assert "distance_km" in cols
    assert "quoted_price" in cols
    assert "status" in cols
    assert "current_location" in cols


def test_parcel_to_dict_fields():
    from app.extensions import db
    from datetime import datetime, timezone
    parcel = Parcel(
        id=1, customer_id=1, pickup_location="A", destination="B",
        weight_category=WeightCategory.medium, distance_km=10, quoted_price=350,
        currency="KES", status=ParcelStatus.pending,
        created_at=datetime.now(timezone.utc), updated_at=datetime.now(timezone.utc),
    )
    d = parcel.to_dict()
    assert "pickupLocation" in d
    assert "destination" in d
    assert "weightCategory" in d
    assert "price" in d
    assert "status" in d
    assert "createdBy" in d
    assert "ownerId" in d
    assert d["weightCategory"] == "medium"
    assert d["weight"] == "Medium (2 - 10kg)"


def test_all_models_importable():
    assert User is not None
    assert Parcel is not None
    assert Driver is not None
    assert Address is not None
    assert PricingRule is not None
    assert Payment is not None
    assert Delivery is not None
    assert TrackingLocation is not None
    assert ParcelStatusHistory is not None
    assert Notification is not None


def test_enum_values():
    assert UserRole.user.value == "user"
    assert UserRole.admin.value == "admin"
    assert ParcelStatus.pending.value == "pending"
    assert ParcelStatus.in_transit.value == "in_transit"
    assert ParcelStatus.delivered.value == "delivered"
    assert ParcelStatus.cancelled.value == "cancelled"
    assert WeightCategory.light.value == "light"
    assert WeightCategory.medium.value == "medium"
    assert WeightCategory.heavy.value == "heavy"
    assert PaymentStatus.pending.value == "pending"
    assert PaymentStatus.completed.value == "completed"
    assert DriverAvailabilityStatus.available.value == "available"
