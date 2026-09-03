from app.models import (
    User, Driver, Address, PricingRule, Parcel,
    ParcelStatusHistory, Delivery, TrackingLocation,
    Payment, Notification,
)
from app.models.enums import (
    UserRole, DriverAvailabilityStatus, ParcelStatus,
    WeightCategory, VehicleCategory, PaymentStatus,
)


def _field_names(model):
    return {f.name for f in model._meta.get_fields()}


def test_user_model_fields():
    cols = _field_names(User)
    assert "id" in cols
    assert "full_name" in cols
    assert "email" in cols
    assert "password_hash" in cols
    assert "role" in cols
    assert "is_active" in cols
    assert "created_at" in cols
    assert "updated_at" in cols


def test_user_to_dict():
    user = User(id=1, full_name="Test", email="t@t.com", role=UserRole.user.value, is_active=True)
    d = user.to_dict()
    assert d["name"] == "Test"
    assert d["role"] == "user"
    assert "id" in d
    assert "email" in d


def test_parcel_model_fields():
    cols = _field_names(Parcel)
    assert "tracking_number" in cols
    assert "customer" in cols
    assert "pickup_location" in cols
    assert "destination" in cols
    assert "weight_kg" in cols
    assert "vehicle_category" in cols
    assert "distance_km" in cols
    assert "quoted_price" in cols
    assert "status" in cols
    assert "current_location" in cols


def test_parcel_to_dict_fields():
    parcel = Parcel(
        id=1, customer_id=1, pickup_location="A", destination="B",
        weight_kg=10, vehicle_category=VehicleCategory.car.value, distance_km=10, quoted_price=350,
        currency="KES", status=ParcelStatus.pending.value,
    )
    d = parcel.to_dict()
    assert "pickupLocation" in d
    assert "destination" in d
    assert "weightKg" in d
    assert "vehicleCategory" in d
    assert "price" in d
    assert "status" in d
    assert "createdBy" in d
    assert "ownerId" in d
    assert d["weightKg"] == 10
    assert d["vehicleCategory"] == "car"


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
    assert VehicleCategory.bike.value == "bike"
    assert VehicleCategory.car.value == "car"
    assert VehicleCategory.lorry.value == "lorry"
    assert PaymentStatus.pending.value == "pending"
    assert PaymentStatus.completed.value == "completed"
    assert DriverAvailabilityStatus.available.value == "available"
