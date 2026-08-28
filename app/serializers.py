from rest_framework import serializers


class SignupRequestSerializer(serializers.Serializer):
    name = serializers.CharField(min_length=1, max_length=255)
    email = serializers.EmailField()
    password = serializers.CharField(min_length=6)
    confirmPassword = serializers.CharField(min_length=6)

    def validate(self, attrs):
        if attrs["password"] != attrs["confirmPassword"]:
            raise serializers.ValidationError(
                {"confirmPassword": "Passwords do not match"}
            )
        return attrs


class LoginRequestSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField()


class CreateParcelRequestSerializer(serializers.Serializer):
    pickupLocation = serializers.CharField(max_length=255)
    destination = serializers.CharField(max_length=255)
    weightCategory = serializers.ChoiceField(choices=["light", "medium", "heavy"])
    distanceKm = serializers.FloatField(min_value=0.1)
    description = serializers.CharField(required=False, allow_null=True, default=None)


class UpdateDestinationRequestSerializer(serializers.Serializer):
    destination = serializers.CharField(min_length=1, max_length=255)


class AdminUpdateStatusRequestSerializer(serializers.Serializer):
    status = serializers.ChoiceField(choices=["pending", "assigned", "in_transit", "delivered"])


class AdminUpdateLocationRequestSerializer(serializers.Serializer):
    currentLocation = serializers.CharField(min_length=1, max_length=255)
