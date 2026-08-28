from rest_framework import generics
from apps.parcels.models import Parcel
from .serializers import AdminParcelSerializer, AdminParcelUpdateSerializer
from .permissions import IsAdminRole


class AdminParcelListView(generics.ListAPIView):
    """GET /api/admin/parcels/ — every parcel in the system, admin-only."""
    queryset = Parcel.objects.select_related('sender').all().order_by('-created_at')
    serializer_class = AdminParcelSerializer
    permission_classes = [IsAdminRole]


class AdminParcelUpdateView(generics.UpdateAPIView):
    """PATCH /api/admin/parcels/<id>/ — update status and/or current location."""
    queryset = Parcel.objects.all()
    serializer_class = AdminParcelUpdateSerializer
    permission_classes = [IsAdminRole]
    http_method_names = ['patch']
