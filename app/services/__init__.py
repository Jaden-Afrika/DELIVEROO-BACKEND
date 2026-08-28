from django.conf import settings

from app.services.geocoding import GeocodingService, OSMGeocodingService, StubGeocodingService
from app.services.routing import OSMRoutingService, RoutingService, StubRoutingService
from app.services.notifications import (
    NotificationService,
    StubNotificationService,
    EmailNotificationService,
)
from app.services.payments import PaymentService, StubPaymentService
from app.services.storage import StorageService, LocalStorageService

_geocoding_service: GeocodingService = None
_routing_service: RoutingService = None
_notification_service: NotificationService = None
_payment_service: PaymentService = None
_storage_service: StorageService = None


def get_geocoding_service() -> GeocodingService:
    global _geocoding_service
    if _geocoding_service is None:
        provider = getattr(settings, "GEOCODING_PROVIDER", "osm")
        if provider == "osm":
            _geocoding_service = OSMGeocodingService()
        else:
            _geocoding_service = StubGeocodingService()
    return _geocoding_service


def get_routing_service() -> RoutingService:
    global _routing_service
    if _routing_service is None:
        provider = getattr(settings, "ROUTING_PROVIDER", "osm")
        if provider == "osm":
            _routing_service = OSMRoutingService()
        else:
            _routing_service = StubRoutingService()
    return _routing_service


def get_notification_service() -> NotificationService:
    global _notification_service
    if _notification_service is None:
        provider = getattr(settings, "NOTIFICATION_PROVIDER", "stub")
        if provider == "email":
            _notification_service = EmailNotificationService()
        else:
            _notification_service = StubNotificationService()
    return _notification_service


def get_payment_service() -> PaymentService:
    global _payment_service
    if _payment_service is None:
        _payment_service = StubPaymentService()
    return _payment_service


def get_storage_service() -> StorageService:
    global _storage_service
    if _storage_service is None:
        _storage_service = LocalStorageService()
    return _storage_service
