import logging
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Optional

import requests

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


class OSMRoutingService(RoutingService):
    """Best-effort driving routes through the public OSRM demo server."""

    ENDPOINT = "https://router.project-osrm.org/route/v1/driving"

    def get_route(
        self, origin_lat: float, origin_lng: float,
        dest_lat: float, dest_lng: float,
    ) -> Optional[RouteResult]:
        try:
            response = requests.get(
                f"{self.ENDPOINT}/{origin_lng},{origin_lat};{dest_lng},{dest_lat}",
                params={"overview": "false"},
                timeout=5,
            )
            response.raise_for_status()
            data = response.json()
        except (requests.RequestException, ValueError) as exc:
            logger.warning("OSRM routing request failed: %s", exc)
            return None

        try:
            if data.get("code") != "Ok" or not data.get("routes"):
                logger.warning("OSRM routing failed: code=%s", data.get("code"))
                return None

            route = data["routes"][0]
            return RouteResult(
                distance_km=float(route["distance"]) / 1000,
                estimated_duration_minutes=float(route["duration"]) / 60,
            )
        except (AttributeError, KeyError, TypeError, ValueError, IndexError) as exc:
            logger.warning("OSRM returned an invalid route: %s", exc)
            return None
