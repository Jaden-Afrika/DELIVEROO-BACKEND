"""Vehicle selection rules shared by parcel creation and pricing."""

from app.models.enums import VehicleCategory


def get_vehicle_category(weight_kg: float) -> str:
    """Return the delivery vehicle category for a parcel weight in kilograms."""
    weight = float(weight_kg)
    if weight < 0:
        raise ValueError("weight_kg must be greater than or equal to zero")
    if weight <= 5:
        return VehicleCategory.bike.value
    if weight <= 50:
        return VehicleCategory.car.value
    return VehicleCategory.lorry.value
