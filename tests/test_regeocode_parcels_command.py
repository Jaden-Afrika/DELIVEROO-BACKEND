from io import StringIO
from unittest.mock import MagicMock, patch

from django.core.management import call_command

from app.models import Parcel
from app.models.enums import ParcelStatus
from app.services.geocoding import GeocodingResult


def _parcel(seed_users):
    return Parcel.objects.create(
        customer=seed_users["user"],
        pickup_location="Sarit Center, Nairobi",
        destination="Prestige Plaza, Nairobi",
        weight_kg=5,
        vehicle_category="bike",
        distance_km=5,
        quoted_price=225,
        status=ParcelStatus.pending.value,
        pickup_latitude=40.7128,
        pickup_longitude=-74.006,
        destination_latitude=-1.2921,
        destination_longitude=36.8219,
    )


@patch("app.management.commands.regeocode_parcels.get_geocoding_service")
def test_command_dry_run_does_not_change_coordinates(mock_get_geocoder, db, seed_users):
    parcel = _parcel(seed_users)
    mock_get_geocoder.return_value.geocode.return_value = GeocodingResult(-1.2676, 36.8108, "Sarit")

    call_command("regeocode_parcels", stdout=StringIO())

    parcel.refresh_from_db()
    assert float(parcel.pickup_latitude) == 40.7128
    assert float(parcel.pickup_longitude) == -74.006


@patch("app.management.commands.regeocode_parcels.get_geocoding_service")
def test_command_repairs_only_out_of_bounds_coordinate_pairs(mock_get_geocoder, db, seed_users):
    parcel = _parcel(seed_users)
    geocoder = MagicMock()
    geocoder.geocode.return_value = GeocodingResult(-1.2676, 36.8108, "Sarit")
    mock_get_geocoder.return_value = geocoder

    call_command("regeocode_parcels", "--apply", stdout=StringIO())

    parcel.refresh_from_db()
    assert float(parcel.pickup_latitude) == -1.2676
    assert float(parcel.pickup_longitude) == 36.8108
    assert float(parcel.destination_latitude) == -1.2921
    assert float(parcel.destination_longitude) == 36.8219
    geocoder.geocode.assert_called_once_with("Sarit Center, Nairobi")
