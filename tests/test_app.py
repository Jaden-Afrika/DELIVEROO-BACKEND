from django.conf import settings


def test_testing_settings_active():
    assert settings.DEBUG is False


def test_health_root(client):
    resp = client.get("/")
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "ok"
    assert data["service"] == "deliveroo-backend"


def test_health_endpoint(client):
    resp = client.get("/health")
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "ok"


def test_openapi_json(client):
    resp = client.get("/openapi.json")
    assert resp.status_code == 200
    data = resp.json()
    assert data["openapi"] == "3.0.3"
    assert "paths" in data
    assert "/auth/signup" in data["paths"]
    assert "/parcels/me" in data["paths"]
    assert "/admin/parcels" in data["paths"]
