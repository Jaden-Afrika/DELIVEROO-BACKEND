"""Repair saved parcel coordinates that do not point to Kenya."""

from django.core.management.base import BaseCommand

from app.models import Parcel
from app.services import get_geocoding_service


KENYA_LATITUDE_RANGE = (-5, 5)
KENYA_LONGITUDE_RANGE = (33, 42)


def is_within_kenya(latitude, longitude):
    """Return whether a coordinate pair is within Kenya's broad bounds."""
    if latitude is None or longitude is None:
        return True
    return (
        KENYA_LATITUDE_RANGE[0] <= float(latitude) <= KENYA_LATITUDE_RANGE[1]
        and KENYA_LONGITUDE_RANGE[0] <= float(longitude) <= KENYA_LONGITUDE_RANGE[1]
    )


class Command(BaseCommand):
    help = "Re-geocode parcel coordinate pairs outside Kenya (dry-run by default)."

    def add_arguments(self, parser):
        parser.add_argument(
            "--apply",
            action="store_true",
            help="Persist corrected coordinates. Without this flag, only report changes.",
        )

    def handle(self, *args, **options):
        apply_changes = options["apply"]
        geocoder = get_geocoding_service()
        repaired = 0
        skipped = 0

        for parcel in Parcel.objects.all().iterator():
            fields_to_update = []
            coordinate_pairs = (
                ("pickup", parcel.pickup_location, "pickup_latitude", "pickup_longitude"),
                ("destination", parcel.destination, "destination_latitude", "destination_longitude"),
            )
            for label, address, latitude_field, longitude_field in coordinate_pairs:
                if is_within_kenya(getattr(parcel, latitude_field), getattr(parcel, longitude_field)):
                    continue

                result = geocoder.geocode(address)
                if result is None or not is_within_kenya(result.latitude, result.longitude):
                    skipped += 1
                    self.stderr.write(
                        f"Parcel {parcel.id}: could not safely repair {label} coordinates."
                    )
                    continue

                setattr(parcel, latitude_field, result.latitude)
                setattr(parcel, longitude_field, result.longitude)
                fields_to_update.extend([latitude_field, longitude_field])
                repaired += 1
                self.stdout.write(f"Parcel {parcel.id}: repaired {label} coordinates.")

            if apply_changes and fields_to_update:
                parcel.save(update_fields=fields_to_update)

        action = "Updated" if apply_changes else "Would update"
        self.stdout.write(self.style.SUCCESS(f"{action} {repaired} coordinate pair(s); skipped {skipped}."))
