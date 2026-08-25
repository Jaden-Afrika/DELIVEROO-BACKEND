import enum


class UserRole(enum.Enum):
    user = "user"
    admin = "admin"


class DriverAvailabilityStatus(enum.Enum):
    available = "available"
    assigned = "assigned"
    offline = "offline"
    suspended = "suspended"


class ParcelStatus(enum.Enum):
    pending = "pending"
    assigned = "assigned"
    in_transit = "in_transit"
    delivered = "delivered"
    cancelled = "cancelled"


class WeightCategory(enum.Enum):
    light = "light"
    medium = "medium"
    heavy = "heavy"


class PaymentStatus(enum.Enum):
    pending = "pending"
    completed = "completed"
    failed = "failed"
    refunded = "refunded"
