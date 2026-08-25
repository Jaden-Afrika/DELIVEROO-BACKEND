from abc import ABC, abstractmethod
from typing import Optional


class NotificationService(ABC):
    @abstractmethod
    def send(self, user_id: int, title: str, message: str, parcel_id: Optional[int] = None) -> dict:
        ...


class StubNotificationService(NotificationService):
    """Deterministic stub for local development and tests."""

    def send(self, user_id: int, title: str, message: str, parcel_id: Optional[int] = None) -> dict:
        return {
            "user_id": user_id,
            "title": title,
            "message": message,
            "parcel_id": parcel_id,
            "sent": True,
            "provider": "stub",
        }
