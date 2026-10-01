from django.contrib.auth import authenticate
from rest_framework import generics, status
from rest_framework.authtoken.models import Token
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from auth_app.api.permissions import IsProfileOwnerOrReadOnly
from auth_app.api.serializers import (
    BusinessProfileListSerializer,
    CustomerProfileListSerializer,
    LoginSerializer,
    ProfileSerializer,
    RegistrationSerializer,
)
from auth_app.models import Profile


def build_auth_payload(user):
    """Returns the token and user info sent after registration or login."""
    token, _ = Token.objects.get_or_create(user=user)
    return {
        "token": token.key,
        "username": user.username,
        "email": user.email,
        "user_id": user.id,
    }


class RegistrationView(APIView):
    """Creates a new business or customer account and returns a token."""

    permission_classes = [AllowAny]

    def post(self, request):
        serializer = RegistrationSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        return Response(
            build_auth_payload(user), status=status.HTTP_201_CREATED
        )


class LoginView(APIView):
    """Authenticates a user by username/password and returns a token."""

    permission_classes = [AllowAny]

    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = authenticate(request, **serializer.validated_data)
        if user is None:
            return Response(
                {"detail": "Invalid credentials."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        return Response(build_auth_payload(user), status=status.HTTP_200_OK)


class ProfileDetailView(generics.RetrieveUpdateAPIView):
    """Shows any profile by user ID; only the owner may edit it."""

    queryset = Profile.objects.select_related("user")
    serializer_class = ProfileSerializer
    permission_classes = [IsAuthenticated, IsProfileOwnerOrReadOnly]
    lookup_field = "user_id"
    lookup_url_kwarg = "pk"
    http_method_names = ["get", "patch"]


class BusinessProfileListView(generics.ListAPIView):
    """Lists all business profiles."""

    queryset = Profile.objects.select_related("user").filter(
        type=Profile.BUSINESS
    )
    serializer_class = BusinessProfileListSerializer


class CustomerProfileListView(generics.ListAPIView):
    """Lists all customer profiles."""

    queryset = Profile.objects.select_related("user").filter(
        type=Profile.CUSTOMER
    )
    serializer_class = CustomerProfileListSerializer
