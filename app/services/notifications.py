from abc import ABC, abstractmethod
from typing import Optional

from django.conf import settings
from django.core.mail import send_mail


class NotificationService(ABC):
    """Base class for delivering parcel notifications to customers.

    Subclasses only implement `send`. The `notify_status_change` and
    `notify_location_change` helpers below build the title/message for
    the two events the spec calls out - an admin changing a parcel's
    status or its current location - and hand off to `send`, so every
    provider gets this behaviour for free.
    """

    @abstractmethod
    def send(
        self,
        user_id: int,
        title: str,
        message: str,
        parcel_id: Optional[int] = None,
        email: Optional[str] = None,
    ) -> dict:
        ...

    def notify_status_change(self, parcel, new_status: str) -> dict:
        title = "Your parcel status has been updated"
        message = (
            f"Your parcel {parcel.tracking_number} is now '{new_status}'. "
            f"Current location: {parcel.current_location or parcel.pickup_location}."
        )
        return self._notify(parcel, title, message)

    def notify_location_change(self, parcel, new_location: str) -> dict:
        title = "Your parcel location has been updated"
        message = f"Your parcel {parcel.tracking_number} is now at '{new_location}'."
        return self._notify(parcel, title, message)

    def _notify(self, parcel, title: str, message: str) -> dict:
        owner = getattr(parcel, "customer", None)
        result = self.send(
            user_id=parcel.customer_id,
            title=title,
            message=message,
            parcel_id=parcel.id,
            email=owner.email if owner else None,
        )
        self._record(parcel, title, message)
        return result

    @staticmethod
    def _record(parcel, title, message):
        """Keep an in-app record of the notification, regardless of whether
        the send itself succeeded, so it isn't lost if email delivery fails."""
        try:
            from app.models import Notification

            Notification.objects.create(
                user_id=parcel.customer_id,
                parcel_id=parcel.id,
                type="email",
                title=title,
                message=message,
            )
        except Exception:
            pass


class StubNotificationService(NotificationService):
    """Deterministic stub for local development and tests. Records the call
    but never actually sends anything over the network."""

    def send(self, user_id, title, message, parcel_id=None, email=None) -> dict:
        return {
            "user_id": user_id,
            "title": title,
            "message": message,
            "parcel_id": parcel_id,
            "sent": True,
            "provider": "stub",
        }


class EmailNotificationService(NotificationService):
    """Sends real emails through Django's configured EMAIL_BACKEND.

    Uses the console backend by default (prints to the server log, useful
    for local development and demos with no mail account required) and
    switches to real SMTP delivery purely through Django's standard
    EMAIL_* settings - see config/settings.py.
    """

    def send(self, user_id, title, message, parcel_id=None, email=None) -> dict:
        if not email:
            return {
                "user_id": user_id,
                "title": title,
                "message": message,
                "parcel_id": parcel_id,
                "sent": False,
                "provider": "email",
                "reason": "No email address on file for this user.",
            }
        try:
            send_mail(
                subject=title,
                message=message,
                from_email=getattr(settings, "DEFAULT_FROM_EMAIL", "no-reply@deliveroo.local"),
                recipient_list=[email],
                fail_silently=False,
            )
            return {
                "user_id": user_id,
                "title": title,
                "message": message,
                "parcel_id": parcel_id,
                "sent": True,
                "provider": "email",
            }
        except Exception as exc:
            return {
                "user_id": user_id,
                "title": title,
                "message": message,
                "parcel_id": parcel_id,
                "sent": False,
                "provider": "email",
                "reason": str(exc),
            }
