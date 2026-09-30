from django.contrib.auth.models import User
from django.db import transaction
from rest_framework import serializers

from auth_app.models import Profile


class RegistrationSerializer(serializers.ModelSerializer):
    """Validates new-account data and creates the user with a profile."""

    password = serializers.CharField(write_only=True)
    repeated_password = serializers.CharField(write_only=True)
    type = serializers.ChoiceField(
        choices=Profile.TYPE_CHOICES, write_only=True
    )

    class Meta:
        model = User
        fields = [
            "username", "email", "password", "repeated_password", "type",
        ]
        extra_kwargs = {"email": {"required": True, "allow_blank": False}}

    def validate_email(self, value):
        if User.objects.filter(email__iexact=value).exists():
            raise serializers.ValidationError(
                "This email is already registered."
            )
        return value

    def validate(self, attrs):
        if attrs["password"] != attrs["repeated_password"]:
            raise serializers.ValidationError("Passwords do not match.")
        return attrs

    @transaction.atomic
    def create(self, validated_data):
        validated_data.pop("repeated_password")
        profile_type = validated_data.pop("type")
        user = User.objects.create_user(**validated_data)
        Profile.objects.create(user=user, type=profile_type)
        return user


class LoginSerializer(serializers.Serializer):
    """Validates login credentials; the view authenticates the user."""

    username = serializers.CharField()
    password = serializers.CharField(write_only=True)
