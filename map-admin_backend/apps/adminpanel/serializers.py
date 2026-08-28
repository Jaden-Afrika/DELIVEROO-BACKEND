from rest_framework import serializers
from apps.parcels.models import Parcel


class AdminParcelSerializer(serializers.ModelSerializer):
    """Full read-only view of a parcel, for the admin table."""
    sender_email = serializers.EmailField(source='sender.email', read_only=True)

    class Meta:
        model = Parcel
        fields = [
            'id', 'sender_email',
            'pickup_location', 'pickup_lat', 'pickup_lng',
            'destination_location', 'destination_lat', 'destination_lng',
            'current_location', 'current_lat', 'current_lng',
            'weight_category', 'price', 'status', 'created_at',
        ]


class AdminParcelUpdateSerializer(serializers.ModelSerializer):
    """Only the fields the inline admin table is allowed to edit."""
    class Meta:
        model = Parcel
        fields = ['status', 'current_location', 'current_lat', 'current_lng']
