def test_dev_geocoding_service():
    from app.services.geocoding import StubGeocodingService
    svc = StubGeocodingService()
    result = svc.geocode("Nairobi")
    assert result is not None
    assert result.latitude == -1.2921
    assert result.longitude == 36.8219
    assert result.formatted_address == "Nairobi"


def test_dev_routing_service():
    from app.services.routing import StubRoutingService
    svc = StubRoutingService()
    result = svc.get_route(0, 0, 1, 1)
    assert result is not None
    assert result.distance_km == 10.0
    assert result.estimated_duration_minutes == 25.0


def test_dev_notification_service():
    from app.services.notifications import StubNotificationService
    svc = StubNotificationService()
    result = svc.send(1, "Test", "Hello")
    assert result["sent"] is True


def test_dev_payment_service():
    from app.services.payments import StubPaymentService
    svc = StubPaymentService()
    result = svc.initiate_payment(100, "KES", 1)
    assert result["status"] == "completed"
    status = svc.get_payment_status("test-txn")
    assert status["status"] == "completed"


def test_dev_storage_service():
    from app.services.storage import LocalStorageService
    svc = LocalStorageService()
    url = svc.get_url("test.txt")
    assert url == "/uploads/test.txt"
