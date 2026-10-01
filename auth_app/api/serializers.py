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


class ProfileSerializer(serializers.ModelSerializer):
    """Full profile including user fields; name and email are editable."""

    username = serializers.CharField(source="user.username", read_only=True)
    first_name = serializers.CharField(
        source="user.first_name", max_length=150,
        required=False, allow_blank=True,
    )
    last_name = serializers.CharField(
        source="user.last_name", max_length=150,
        required=False, allow_blank=True,
    )
    email = serializers.EmailField(source="user.email", required=False)

    class Meta:
        model = Profile
        fields = [
            "user", "username", "first_name", "last_name", "file",
            "location", "tel", "description", "working_hours", "type",
            "email", "created_at",
        ]
        read_only_fields = ["user", "type", "created_at"]

    def validate_email(self, value):
        others = User.objects.exclude(pk=self.instance.user_id)
        if others.filter(email__iexact=value).exists():
            raise serializers.ValidationError(
                "This email is already registered."
            )
        return value

    @transaction.atomic
    def update(self, instance, validated_data):
        user_data = validated_data.pop("user", {})
        for attr, value in user_data.items():
            setattr(instance.user, attr, value)
        instance.user.save()
        return super().update(instance, validated_data)


class BusinessProfileListSerializer(ProfileSerializer):
    """Business profile as shown in the public business user list."""

    class Meta(ProfileSerializer.Meta):
        fields = [
            "user", "username", "first_name", "last_name", "file",
            "location", "tel", "description", "working_hours", "type",
        ]


class CustomerProfileListSerializer(ProfileSerializer):
    """Customer profile as shown in the customer user list."""

    uploaded_at = serializers.DateTimeField(
        source="created_at", read_only=True
    )

    class Meta(ProfileSerializer.Meta):
        fields = [
            "user", "username", "first_name", "last_name", "file",
            "uploaded_at", "type",
        ]
