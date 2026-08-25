from datetime import datetime, timezone

from app.extensions import db
from app.models.enums import ParcelStatus


class ParcelStatusHistory(db.Model):
    __tablename__ = "parcel_status_history"

    id = db.Column(db.Integer, primary_key=True)
    parcel_id = db.Column(db.Integer, db.ForeignKey("parcels.id"), nullable=False)
    status = db.Column(db.Enum(ParcelStatus), nullable=False)
    changed_by_user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=True)
    notes = db.Column(db.Text, nullable=True)
    created_at = db.Column(
        db.DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc)
    )
