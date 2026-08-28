import logging
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Optional

import requests
from django.conf import settings

logger = logging.getLogger(__name__)


@dataclass
class RouteResult:
    distance_km: float
    estimated_duration_minutes: float


class RoutingService(ABC):
    @abstractmethod
    def get_route(
        self, origin_lat: float, origin_lng: float,
        dest_lat: float, dest_lng: float,
    ) -> Optional[RouteResult]:
        ...


class StubRoutingService(RoutingService):
    """Deterministic stub: returns 10 km / 25 min."""

    def get_route(
        self, origin_lat: float, origin_lng: float,
        dest_lat: float, dest_lng: float,
    ) -> Optional[RouteResult]:
        return RouteResult(distance_km=10.0, estimated_duration_minutes=25.0)


class GoogleRoutingService(RoutingService):
    """Real driving distance/duration via the Google Directions API.

    Requires GOOGLE_MAPS_API_KEY to be set. Like GoogleGeocodingService,
    returns None on any failure rather than raising, since callers treat
    a missing route as non-fatal and fall back to whatever distance/price
    was already on the parcel.
    """

    ENDPOINT = "https://maps.googleapis.com/maps/api/directions/json"

    def get_route(
        self, origin_lat: float, origin_lng: float,
        dest_lat: float, dest_lng: float,
    ) -> Optional[RouteResult]:
        api_key = getattr(settings, "GOOGLE_MAPS_API_KEY", "")
        if not api_key:
            logger.warning("GOOGLE_MAPS_API_KEY is not set; cannot compute route")
            return None
        try:
            resp = requests.get(
                self.ENDPOINT,
                params={
                    "origin": f"{origin_lat},{origin_lng}",
                    "destination": f"{dest_lat},{dest_lng}",
                    "key": api_key,
                },
                timeout=5,
            )
            resp.raise_for_status()
            data = resp.json()
        except requests.RequestException as exc:
            logger.warning("Directions request failed: %s", exc)
            return None

        if data.get("status") != "OK" or not data.get("routes"):
            logger.warning("Directions failed: status=%s", data.get("status"))
            return None

        leg = data["routes"][0]["legs"][0]
        return RouteResult(
            distance_km=leg["distance"]["value"] / 1000,
            estimated_duration_minutes=leg["duration"]["value"] / 60,
        )
