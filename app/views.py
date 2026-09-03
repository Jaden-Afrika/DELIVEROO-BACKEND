from datetime import datetime, timezone

from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import AccessToken

from app.exceptions import ValidationError422, ConflictError
from app.models.enums import ParcelStatus
from app.models import Parcel, ParcelStatusHistory, User
from app.serializers import (
    SignupRequestSerializer,
    LoginRequestSerializer,
    CreateParcelRequestSerializer,
    UpdateDestinationRequestSerializer,
    AdminUpdateStatusRequestSerializer,
    AdminUpdateLocationRequestSerializer,
)
from app.services.auth import create_user, authenticate_user
from app.services.pricing import calculate_price
from app.services.vehicle import get_vehicle_category
from app.services import get_geocoding_service, get_routing_service, get_notification_service


def _serialize_validation(errors):
    details = {}
    for field, list_of_msgs in errors.items():
        details[field] = list_of_msgs if isinstance(list_of_msgs, list) else [str(list_of_msgs)]
    return details


class SignupView(APIView):
    permission_classes = [~IsAuthenticated]

    def post(self, request):
        serializer = SignupRequestSerializer(data=request.data)
        if not serializer.is_valid():
            raise ValidationError422(_serialize_validation(serializer.errors))

        data = serializer.validated_data
        if User.objects.filter(email=data["email"]).exists():
            raise ConflictError({"error": "Email already registered"})

        user = create_user(
            full_name=data["name"],
            email=data["email"],
            password=data["password"],
        )
        token = AccessToken.for_user(user)
        return Response(
            {"access_token": str(token), "user": user.to_dict()},
            status=status.HTTP_201_CREATED,
        )


class LoginView(APIView):
    permission_classes = [~IsAuthenticated]

    def post(self, request):
        serializer = LoginRequestSerializer(data=request.data)
        if not serializer.is_valid():
            raise ValidationError422(_serialize_validation(serializer.errors))

        data = serializer.validated_data
        user = authenticate_user(data["email"], data["password"])
        if user is None:
            return Response({"error": "Invalid email or password"}, status=401)
        if not user.is_active:
            return Response({"error": "Account deactivated"}, status=403)

        token = AccessToken.for_user(user)
        return Response({"access_token": str(token), "user": user.to_dict()}, status=200)


class LogoutView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        return Response({"message": "Logged out"}, status=200)


class MeView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        return Response({"user": request.user.to_dict()}, status=200)


class ListMyParcelsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        parcels = Parcel.objects.filter(customer_id=request.user.id)
        return Response([p.to_dict() for p in parcels], status=200)


class CreateParcelView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = CreateParcelRequestSerializer(data=request.data)
        if not serializer.is_valid():
            raise ValidationError422(_serialize_validation(serializer.errors))

        data = serializer.validated_data
        weight_kg = data["weight_kg"]
        vehicle_category = get_vehicle_category(weight_kg)
        pricing = calculate_price(weight_kg, data["distanceKm"])

        parcel = Parcel(
            customer_id=request.user.id,
            weight_kg=weight_kg,
            vehicle_category=vehicle_category,
            pickup_location=data["pickupLocation"],
            destination=data["destination"],
            distance_km=data["distanceKm"],
            quoted_price=pricing["total"],
            currency=pricing["currency"],
            description=data.get("description"),
        )

        # Best-effort geocoding so the map has pickup/destination coordinates
        # to plot from the moment the parcel is created. A geocoding failure
        # should never block parcel creation, so this stays non-fatal.
        try:
            geocoder = get_geocoding_service()
            pickup_geo = geocoder.geocode(data["pickupLocation"])
            dest_geo = geocoder.geocode(data["destination"])
            if pickup_geo:
                parcel.pickup_latitude = pickup_geo.latitude
                parcel.pickup_longitude = pickup_geo.longitude
            if dest_geo:
                parcel.destination_latitude = dest_geo.latitude
                parcel.destination_longitude = dest_geo.longitude
        except Exception:
            pass

        parcel.save()

        ParcelStatusHistory.objects.create(
            parcel=parcel,
            status=ParcelStatus.pending.value,
            changed_by_user_id=request.user.id,
            notes="Parcel created",
        )

        return Response(parcel.to_dict(), status=status.HTTP_201_CREATED)


def _get_parcel_or_none(parcel_id):
    try:
        return Parcel.objects.get(pk=parcel_id)
    except Parcel.DoesNotExist:
        return None


def _is_owner_or_admin(parcel, user):
    if parcel.customer_id == user.id:
        return True
    if user.role == "admin":
        return True
    return False


def _can_access(parcel, user):
    return parcel is not None and _is_owner_or_admin(parcel, user)


class ParcelDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, parcel_id):
        parcel = _get_parcel_or_none(parcel_id)
        if not _can_access(parcel, request.user):
            return Response(
                {"error": {"code": "PARCEL_NOT_FOUND", "message": "Parcel not found."}}, status=404
            )
        return Response(parcel.to_dict(), status=200)


class UpdateDestinationView(APIView):
    permission_classes = [IsAuthenticated]

    def patch(self, request, parcel_id):
        parcel = _get_parcel_or_none(parcel_id)
        if not _can_access(parcel, request.user):
            return Response(
                {"error": {"code": "PARCEL_NOT_FOUND", "message": "Parcel not found."}}, status=404
            )

        if parcel.status == ParcelStatus.delivered.value:
            raise ConflictError({
                "error": {"code": "PARCEL_DELIVERED", "message": "Cannot update destination for a delivered parcel."}
            })
        if parcel.status == ParcelStatus.cancelled.value:
            raise ConflictError({
                "error": {"code": "PARCEL_CANCELLED", "message": "Cannot update destination for a cancelled parcel."}
            })

        serializer = UpdateDestinationRequestSerializer(data=request.data)
        if not serializer.is_valid():
            raise ValidationError422(_serialize_validation(serializer.errors))

        new_destination = serializer.validated_data["destination"]
        if new_destination.strip() == (parcel.destination or "").strip():
            return Response(parcel.to_dict(), status=200)

        try:
            geocoder = get_geocoding_service()
            router = get_routing_service()

            pickup_geo = geocoder.geocode(parcel.pickup_location)
            dest_geo = geocoder.geocode(new_destination)

            if pickup_geo and dest_geo:
                route = router.get_route(
                    pickup_geo.latitude, pickup_geo.longitude,
                    dest_geo.latitude, dest_geo.longitude,
                )
                if route:
                    parcel.distance_km = route.distance_km
                    parcel.duration_minutes = route.estimated_duration_minutes
                    pricing = calculate_price(parcel.weight_kg, route.distance_km)
                    parcel.quoted_price = pricing["total"]
                    parcel.currency = pricing["currency"]

            parcel.destination = new_destination
            if dest_geo:
                parcel.destination_latitude = dest_geo.latitude
                parcel.destination_longitude = dest_geo.longitude
                parcel.current_location = dest_geo.formatted_address

            parcel.save()

            ParcelStatusHistory.objects.create(
                parcel=parcel,
                status=parcel.status,
                changed_by_user_id=request.user.id,
                notes=f"Destination changed to: {new_destination}",
            )
        except Exception:
            return Response(
                {"error": {"code": "UPDATE_FAILED", "message": "Failed to update destination."}},
                status=500,
            )

        return Response(parcel.to_dict(), status=200)


class CancelParcelView(APIView):
    permission_classes = [IsAuthenticated]

    def patch(self, request, parcel_id):
        parcel = _get_parcel_or_none(parcel_id)
        if not _can_access(parcel, request.user):
            return Response(
                {"error": {"code": "PARCEL_NOT_FOUND", "message": "Parcel not found."}}, status=404
            )

        if parcel.status == ParcelStatus.delivered.value:
            raise ConflictError({
                "error": {"code": "PARCEL_DELIVERED", "message": "Cannot cancel a delivered parcel."}
            })
        if parcel.status == ParcelStatus.cancelled.value:
            raise ConflictError({
                "error": {"code": "PARCEL_CANCELLED", "message": "Parcel is already cancelled."}
            })

        try:
            parcel.status = ParcelStatus.cancelled.value
            parcel.cancelled_at = datetime.now(timezone.utc)
            parcel.save()
            ParcelStatusHistory.objects.create(
                parcel=parcel,
                status=ParcelStatus.cancelled.value,
                changed_by_user_id=request.user.id,
                notes="Parcel cancelled by owner",
            )
        except Exception:
            return Response(
                {"error": {"code": "CANCEL_FAILED", "message": "Failed to cancel parcel."}}, status=500
            )

        return Response(parcel.to_dict(), status=200)


class StatusHistoryView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, parcel_id):
        parcel = _get_parcel_or_none(parcel_id)
        if not _can_access(parcel, request.user):
            return Response(
                {"error": {"code": "PARCEL_NOT_FOUND", "message": "Parcel not found."}}, status=404
            )

        history = ParcelStatusHistory.objects.filter(parcel_id=parcel.id).order_by("created_at")
        return Response([
            {
                "id": h.id,
                "status": h.status,
                "changedByUserId": h.changed_by_user_id,
                "notes": h.notes,
                "createdAt": h.created_at.astimezone(timezone.utc).isoformat() if h.created_at else None,
            }
            for h in history
        ], status=200)


class TrackingView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, parcel_id):
        parcel = _get_parcel_or_none(parcel_id)
        if not _can_access(parcel, request.user):
            return Response(
                {"error": {"code": "PARCEL_NOT_FOUND", "message": "Parcel not found."}}, status=404
            )

        last_update = (
            ParcelStatusHistory.objects.filter(parcel_id=parcel.id).order_by("-created_at").first()
        )

        return Response(
            {
                "parcelId": parcel.id,
                "status": parcel.status,
                "pickup": {
                    "label": parcel.pickup_location,
                    "latitude": float(parcel.pickup_latitude) if parcel.pickup_latitude is not None else None,
                    "longitude": float(parcel.pickup_longitude) if parcel.pickup_longitude is not None else None,
                },
                "destination": {
                    "label": parcel.destination,
                    "latitude": float(parcel.destination_latitude) if parcel.destination_latitude is not None else None,
                    "longitude": float(parcel.destination_longitude) if parcel.destination_longitude is not None else None,
                },
                "currentLocation": parcel.current_location,
                "distanceKm": float(parcel.distance_km) if parcel.distance_km is not None else None,
                "estimatedTravelTime": parcel._estimated_travel_minutes(),
                "lastUpdatedAt": Parcel._iso(last_update.created_at) if last_update else Parcel._iso(parcel.updated_at),
                "lastUpdateNote": last_update.notes if last_update else None,
            },
            status=200,
        )


class AdminListParcelsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        if request.user.role != "admin":
            return Response({"error": "Admin access required"}, status=403)
        parcels = Parcel.objects.all().order_by("-created_at")
        return Response([p.to_dict() for p in parcels], status=200)


class AdminUpdateStatusView(APIView):
    permission_classes = [IsAuthenticated]

    def patch(self, request, parcel_id):
        if request.user.role != "admin":
            return Response({"error": "Admin access required"}, status=403)

        parcel = _get_parcel_or_none(parcel_id)
        if parcel is None:
            return Response(
                {"error": {"code": "PARCEL_NOT_FOUND", "message": "Parcel not found."}}, status=404
            )

        serializer = AdminUpdateStatusRequestSerializer(data=request.data)
        if not serializer.is_valid():
            raise ValidationError422(_serialize_validation(serializer.errors))

        new_status = serializer.validated_data["status"]
        if parcel.status == new_status:
            return Response(parcel.to_dict(), status=200)

        parcel.status = new_status
        if new_status == ParcelStatus.delivered.value:
            parcel.delivered_at = datetime.now(timezone.utc)
        parcel.save()

        ParcelStatusHistory.objects.create(
            parcel=parcel,
            status=new_status,
            changed_by_user_id=request.user.id,
            notes=f"Status changed to {new_status} by admin",
        )

        get_notification_service().notify_status_change(parcel, new_status)

        return Response(parcel.to_dict(), status=200)


class AdminUpdateLocationView(APIView):
    permission_classes = [IsAuthenticated]

    def patch(self, request, parcel_id):
        if request.user.role != "admin":
            return Response({"error": "Admin access required"}, status=403)

        parcel = _get_parcel_or_none(parcel_id)
        if parcel is None:
            return Response(
                {"error": {"code": "PARCEL_NOT_FOUND", "message": "Parcel not found."}}, status=404
            )

        serializer = AdminUpdateLocationRequestSerializer(data=request.data)
        if not serializer.is_valid():
            raise ValidationError422(_serialize_validation(serializer.errors))

        new_location = serializer.validated_data["currentLocation"]
        parcel.current_location = new_location
        parcel.save()

        get_notification_service().notify_location_change(parcel, new_location)

        return Response(parcel.to_dict(), status=200)
