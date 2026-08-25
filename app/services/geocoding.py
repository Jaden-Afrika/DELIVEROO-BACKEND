from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Optional


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
