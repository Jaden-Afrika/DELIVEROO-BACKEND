"""URL configuration for the Deliveroo backend."""
from django.contrib import admin
from django.http import JsonResponse
from django.urls import include, path


def health(request):
    return JsonResponse({"status": "ok", "service": "deliveroo-backend"})


OPENAPI_SPEC = {
    "openapi": "3.0.3",
    "info": {
        "title": "Deliveroo Backend API",
        "version": "0.1.0",
        "description": "Courier parcel delivery API",
    },
    "paths": {
        "/auth/signup": {"post": {"summary": "Register a new user", "tags": ["auth"]}},
        "/auth/login": {"post": {"summary": "Log in", "tags": ["auth"]}},
        "/auth/logout": {"post": {"summary": "Log out", "tags": ["auth"]}},
        "/auth/me": {"get": {"summary": "Current user", "tags": ["auth"]}},
        "/parcels/me": {"get": {"summary": "List my parcels", "tags": ["parcels"]}},
        "/parcels": {
            "post": {"summary": "Create parcel", "tags": ["parcels"]},
            "get": {"summary": "List parcels", "tags": ["parcels"]},
        },
        "/parcels/{id}": {"get": {"summary": "Get parcel", "tags": ["parcels"]}},
        "/parcels/{id}/destination": {"patch": {"summary": "Update destination", "tags": ["parcels"]}},
        "/parcels/{id}/cancel": {"patch": {"summary": "Cancel parcel", "tags": ["parcels"]}},
        "/parcels/{id}/status-history": {"get": {"summary": "Status history", "tags": ["parcels"]}},
        "/parcels/{id}/tracking": {"get": {"summary": "Tracking", "tags": ["parcels"]}},
        "/admin/parcels": {"get": {"summary": "List all parcels (admin)", "tags": ["admin"]}},
        "/admin/parcels/{id}/status": {"patch": {"summary": "Update status (admin)", "tags": ["admin"]}},
        "/admin/parcels/{id}/location": {"patch": {"summary": "Update location (admin)", "tags": ["admin"]}},
    },
}


def openapi(request):
    return JsonResponse(OPENAPI_SPEC)


urlpatterns = [
    path("django-admin/", admin.site.urls),
    path("", include("app.urls")),
    path("", health),
    path("health", health),
    path("openapi.json", openapi),
]
