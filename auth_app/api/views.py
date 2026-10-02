from django.contrib.auth import authenticate
from django.db.models import Avg
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
from offers_app.models import Offer
from reviews_app.models import Review


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
        """Registers a user and returns the auth token."""
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
        """Checks the credentials and returns the auth token."""
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
    permission_classes = [IsAuthenticated]


class CustomerProfileListView(generics.ListAPIView):
    """Lists all customer profiles."""

    queryset = Profile.objects.select_related("user").filter(
        type=Profile.CUSTOMER
    )
    serializer_class = CustomerProfileListSerializer
    permission_classes = [IsAuthenticated]


class BaseInfoView(APIView):
    """Public platform statistics shown on the landing page."""

    permission_classes = [AllowAny]

    def get(self, request):
        """Returns review, profile and offer statistics."""
        average = Review.objects.aggregate(avg=Avg("rating"))["avg"]
        return Response({
            "review_count": Review.objects.count(),
            "average_rating": round(average or 0, 1),
            "business_profile_count": Profile.objects.filter(
                type=Profile.BUSINESS
            ).count(),
            "offer_count": Offer.objects.count(),
        })
