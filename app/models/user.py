from datetime import datetime, timezone

from app.extensions import db
from app.models.enums import UserRole


class User(db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    full_name = db.Column(db.String(255), nullable=False)
    email = db.Column(db.String(255), nullable=False, unique=True, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    phone_number = db.Column(db.String(50), nullable=True)
    role = db.Column(db.Enum(UserRole), nullable=False, default=UserRole.user)
    is_active = db.Column(db.Boolean, nullable=False, default=True)
    created_at = db.Column(
        db.DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc)
    )
    updated_at = db.Column(
        db.DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    addresses = db.relationship("Address", backref="user", lazy=True)
    driver_profile = db.relationship("Driver", backref="user", uselist=False, lazy=True)
    parcels = db.relationship("Parcel", backref="customer", lazy=True, foreign_keys="Parcel.customer_id")

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.full_name,
            "email": self.email,
            "role": self.role.value,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }
