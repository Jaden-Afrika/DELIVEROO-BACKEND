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
    # ``weight`` is the frontend contract. ``weightKg`` remains supported for
    # existing API consumers while they migrate to the canonical field.
    weight = serializers.FloatField(min_value=0, required=False)
    weightKg = serializers.FloatField(min_value=0, required=False)
    distanceKm = serializers.FloatField(min_value=0.1)
    description = serializers.CharField(required=False, allow_null=True, default=None)

    def validate(self, attrs):
        weight = attrs.get("weight")
        weight_kg = attrs.get("weightKg")
        if weight is None and weight_kg is None:
            raise serializers.ValidationError({"weight": "This field is required."})
        if weight is not None and weight_kg is not None and weight != weight_kg:
            raise serializers.ValidationError({"weight": "Must match weightKg when both are provided."})
        attrs["weight_kg"] = weight if weight is not None else weight_kg
        return attrs


class UpdateDestinationRequestSerializer(serializers.Serializer):
    destination = serializers.CharField(min_length=1, max_length=255)

    def validate_destination(self, value):
        value = value.strip()
        if not value:
            raise serializers.ValidationError("Destination must not be blank.")
        return value


class AdminUpdateStatusRequestSerializer(serializers.Serializer):
    status = serializers.ChoiceField(choices=["pending", "assigned", "in_transit", "delivered"])


class AdminUpdateLocationRequestSerializer(serializers.Serializer):
    currentLocation = serializers.CharField(min_length=1, max_length=255)
