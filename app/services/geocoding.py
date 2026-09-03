import logging
import threading
import time
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Optional

import requests

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


class OSMGeocodingService(GeocodingService):
    """Best-effort address geocoding through OpenStreetMap's Nominatim API.

    Nominatim permits at most one request per second. The application uses a
    singleton service through ``get_geocoding_service()``, and this instance
    serializes and spaces its requests accordingly. Errors remain non-fatal so
    parcel creation continues when the public service is unavailable.
    """

    ENDPOINT = "https://nominatim.openstreetmap.org/search"
    USER_AGENT = "deliveroo-backend/1.0 (OpenStreetMap geocoding)"
    MIN_REQUEST_INTERVAL_SECONDS = 1.0

    def __init__(self):
        self._last_request_at: Optional[float] = None
        self._rate_limit_lock = threading.Lock()

    def _respect_rate_limit(self) -> None:
        """Wait until this service's next request is within Nominatim's limit."""
        with self._rate_limit_lock:
            if self._last_request_at is not None:
                elapsed = time.monotonic() - self._last_request_at
                delay = self.MIN_REQUEST_INTERVAL_SECONDS - elapsed
                if delay > 0:
                    time.sleep(delay)
            self._last_request_at = time.monotonic()

    def geocode(self, address_text: str) -> Optional[GeocodingResult]:
        if not address_text or not address_text.strip():
            return None

        try:
            self._respect_rate_limit()
            response = requests.get(
                self.ENDPOINT,
                params={
                    "q": address_text,
                    "format": "json",
                    "limit": 1,
                    "countrycodes": "ke",
                },
                headers={"User-Agent": self.USER_AGENT},
                timeout=5,
            )
            response.raise_for_status()
            results = response.json()
            if not results:
                logger.warning("Nominatim returned no result for '%s'", address_text)
                return None

            result = results[0]
            return GeocodingResult(
                latitude=float(result["lat"]),
                longitude=float(result["lon"]),
                formatted_address=result.get("display_name", address_text),
            )
        except (
            requests.RequestException,
            ValueError,
            KeyError,
            TypeError,
            IndexError,
            AttributeError,
        ) as exc:
            logger.warning("Nominatim geocoding failed for '%s': %s", address_text, exc)
            return None
