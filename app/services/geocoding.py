import logging
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Optional

import requests
from django.conf import settings

logger = logging.getLogger(__name__)


@dataclass
class GeocodingResult:
    latitude: float
    longitude: float
    formatted_address: str


class GeocodingService(ABC):
    @abstractmethod
    def geocode(self, address_text: str) -> Optional[GeocodingResult]:
        ...


class StubGeocodingService(GeocodingService):
    """Deterministic stub for local development and tests."""

    def geocode(self, address_text: str) -> Optional[GeocodingResult]:
        return GeocodingResult(
            latitude=-1.2921,
            longitude=36.8219,
            formatted_address=address_text,
        )


class GoogleGeocodingService(GeocodingService):
    """Real geocoding via the Google Geocoding API.

    Requires GOOGLE_MAPS_API_KEY to be set. Callers already treat a
    failed/None geocode as non-fatal (see views.py), so this returns
    None on any error rather than raising - a bad address or a network
    hiccup should never block parcel creation.
    """

    ENDPOINT = "https://maps.googleapis.com/maps/api/geocode/json"

    def geocode(self, address_text: str) -> Optional[GeocodingResult]:
        api_key = getattr(settings, "GOOGLE_MAPS_API_KEY", "")
        if not api_key:
            logger.warning("GOOGLE_MAPS_API_KEY is not set; cannot geocode '%s'", address_text)
            return None
        try:
            resp = requests.get(
                self.ENDPOINT,
                params={"address": address_text, "key": api_key},
                timeout=5,
            )
            resp.raise_for_status()
            data = resp.json()
        except requests.RequestException as exc:
            logger.warning("Geocoding request failed for '%s': %s", address_text, exc)
            return None

        if data.get("status") != "OK" or not data.get("results"):
            logger.warning(
                "Geocoding failed for '%s': status=%s", address_text, data.get("status")
            )
            return None

        result = data["results"][0]
        location = result["geometry"]["location"]
        return GeocodingResult(
            latitude=location["lat"],
            longitude=location["lng"],
            formatted_address=result.get("formatted_address", address_text),
        )
