from django.urls import resolve


def _resolves(path):
    try:
        resolve(path)
        return True
    except Exception:
        return False


def test_route_registration():
    assert _resolves("/auth/signup")
    assert _resolves("/auth/login")
    assert _resolves("/auth/logout")
    assert _resolves("/auth/me")
    assert _resolves("/parcels/me")
    assert _resolves("/parcels")
    assert _resolves("/parcels/1")
    assert _resolves("/parcels/1/cancel")
    assert _resolves("/parcels/1/destination")
    assert _resolves("/parcels/1/status-history")
    assert _resolves("/parcels/1/tracking")
    assert _resolves("/admin/parcels")
    assert _resolves("/admin/parcels/1/status")
    assert _resolves("/admin/parcels/1/location")
    assert _resolves("/")
    assert _resolves("/health")
    assert _resolves("/openapi.json")
