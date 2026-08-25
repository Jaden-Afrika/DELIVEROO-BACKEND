from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Optional


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
