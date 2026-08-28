from unittest.mock import patch, MagicMock

from django.test import override_settings

from app.services.geocoding import GoogleGeocodingService
from app.services.routing import GoogleRoutingService


def _mock_response(json_data, status_code=200):
    resp = MagicMock()
    resp.status_code = status_code
    resp.json.return_value = json_data
    resp.raise_for_status.side_effect = None
    return resp


class TestGoogleGeocodingService:
    @override_settings(GOOGLE_MAPS_API_KEY="")
    def test_returns_none_without_api_key(self):
        svc = GoogleGeocodingService()
        assert svc.geocode("Nairobi") is None

    @override_settings(GOOGLE_MAPS_API_KEY="test-key")
    @patch("app.services.geocoding.requests.get")
    def test_parses_successful_response(self, mock_get):
        mock_get.return_value = _mock_response({
            "status": "OK",
            "results": [{
                "formatted_address": "Nairobi, Kenya",
                "geometry": {"location": {"lat": -1.286389, "lng": 36.817223}},
            }],
        })
        svc = GoogleGeocodingService()
        result = svc.geocode("Nairobi")
        assert result is not None
        assert result.latitude == -1.286389
        assert result.longitude == 36.817223
        assert result.formatted_address == "Nairobi, Kenya"

    @override_settings(GOOGLE_MAPS_API_KEY="test-key")
    @patch("app.services.geocoding.requests.get")
    def test_returns_none_on_zero_results(self, mock_get):
        mock_get.return_value = _mock_response({"status": "ZERO_RESULTS", "results": []})
        svc = GoogleGeocodingService()
        assert svc.geocode("nonexistent place xyz") is None

    @override_settings(GOOGLE_MAPS_API_KEY="test-key")
    @patch("app.services.geocoding.requests.get")
    def test_returns_none_on_request_exception(self, mock_get):
        import requests
        mock_get.side_effect = requests.RequestException("network error")
        svc = GoogleGeocodingService()
        assert svc.geocode("Nairobi") is None


class TestGoogleRoutingService:
    @override_settings(GOOGLE_MAPS_API_KEY="")
    def test_returns_none_without_api_key(self):
        svc = GoogleRoutingService()
        assert svc.get_route(0, 0, 1, 1) is None

    @override_settings(GOOGLE_MAPS_API_KEY="test-key")
    @patch("app.services.routing.requests.get")
    def test_parses_successful_response(self, mock_get):
        mock_get.return_value = _mock_response({
            "status": "OK",
            "routes": [{
                "legs": [{
                    "distance": {"value": 12500},
                    "duration": {"value": 1500},
                }]
            }],
        })
        svc = GoogleRoutingService()
        result = svc.get_route(-1.28, 36.82, -1.30, 36.78)
        assert result is not None
        assert result.distance_km == 12.5
        assert result.estimated_duration_minutes == 25.0

    @override_settings(GOOGLE_MAPS_API_KEY="test-key")
    @patch("app.services.routing.requests.get")
    def test_returns_none_on_no_routes(self, mock_get):
        mock_get.return_value = _mock_response({"status": "ZERO_RESULTS", "routes": []})
        svc = GoogleRoutingService()
        assert svc.get_route(0, 0, 1, 1) is None
