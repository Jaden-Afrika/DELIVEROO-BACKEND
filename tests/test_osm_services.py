from unittest.mock import MagicMock, patch

import requests
from django.test import override_settings

import app.services as services
from app.services.geocoding import OSMGeocodingService
from app.services.routing import OSMRoutingService


def _mock_response(json_data):
    response = MagicMock()
    response.json.return_value = json_data
    response.raise_for_status.return_value = None
    return response


class TestOSMGeocodingService:
    @patch("app.services.geocoding.requests.get")
    def test_parses_successful_nominatim_response(self, mock_get):
        mock_get.return_value = _mock_response([{
            "lat": "-1.286389",
            "lon": "36.817223",
            "display_name": "Nairobi, Kenya",
        }])

        result = OSMGeocodingService().geocode("Nairobi")

        assert result is not None
        assert result.latitude == -1.286389
        assert result.longitude == 36.817223
        assert result.formatted_address == "Nairobi, Kenya"
        mock_get.assert_called_once_with(
            OSMGeocodingService.ENDPOINT,
            params={"q": "Nairobi", "format": "json", "limit": 1},
            headers={"User-Agent": OSMGeocodingService.USER_AGENT},
            timeout=5,
        )

    @patch("app.services.geocoding.requests.get")
    def test_returns_none_for_empty_results(self, mock_get):
        mock_get.return_value = _mock_response([])
        assert OSMGeocodingService().geocode("nonexistent place xyz") is None

    @patch("app.services.geocoding.requests.get", side_effect=requests.Timeout)
    def test_returns_none_on_request_failure(self, mock_get):
        assert OSMGeocodingService().geocode("Nairobi") is None

    @patch("app.services.geocoding.requests.get")
    def test_returns_none_for_non_success_response(self, mock_get):
        response = _mock_response([])
        response.raise_for_status.side_effect = requests.HTTPError("503")
        mock_get.return_value = response
        assert OSMGeocodingService().geocode("Nairobi") is None

    @patch("app.services.geocoding.time.sleep")
    @patch("app.services.geocoding.time.monotonic", side_effect=[10.0, 10.5, 11.0])
    @patch("app.services.geocoding.requests.get")
    def test_spaces_repeated_requests_by_one_second(self, mock_get, mock_monotonic, mock_sleep):
        mock_get.return_value = _mock_response([])
        service = OSMGeocodingService()

        service.geocode("Nairobi")
        service.geocode("Mombasa")

        mock_sleep.assert_called_once_with(0.5)


class TestOSMRoutingService:
    @patch("app.services.routing.requests.get")
    def test_parses_successful_osrm_response(self, mock_get):
        mock_get.return_value = _mock_response({
            "code": "Ok",
            "routes": [{"distance": 12500, "duration": 1500}],
        })

        result = OSMRoutingService().get_route(-1.28, 36.82, -1.30, 36.78)

        assert result is not None
        assert result.distance_km == 12.5
        assert result.estimated_duration_minutes == 25.0
        mock_get.assert_called_once_with(
            "https://router.project-osrm.org/route/v1/driving/36.82,-1.28;36.78,-1.3",
            params={"overview": "false"},
            timeout=5,
        )

    @patch("app.services.routing.requests.get")
    def test_returns_none_when_osrm_has_no_route(self, mock_get):
        mock_get.return_value = _mock_response({"code": "NoRoute", "routes": []})
        assert OSMRoutingService().get_route(0, 0, 1, 1) is None

    @patch("app.services.routing.requests.get", side_effect=requests.Timeout)
    def test_returns_none_on_request_failure(self, mock_get):
        assert OSMRoutingService().get_route(0, 0, 1, 1) is None

    @patch("app.services.routing.requests.get")
    def test_returns_none_for_non_success_response(self, mock_get):
        response = _mock_response({})
        response.raise_for_status.side_effect = requests.HTTPError("503")
        mock_get.return_value = response
        assert OSMRoutingService().get_route(0, 0, 1, 1) is None


@override_settings(GEOCODING_PROVIDER="osm", ROUTING_PROVIDER="osm")
def test_factories_select_osm_services():
    previous_geocoder = services._geocoding_service
    previous_router = services._routing_service
    try:
        services._geocoding_service = None
        services._routing_service = None

        assert isinstance(services.get_geocoding_service(), OSMGeocodingService)
        assert isinstance(services.get_routing_service(), OSMRoutingService)
    finally:
        services._geocoding_service = previous_geocoder
        services._routing_service = previous_router
