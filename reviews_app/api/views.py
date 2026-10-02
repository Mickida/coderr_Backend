from django.db import IntegrityError, transaction
from rest_framework import generics
from rest_framework.exceptions import ValidationError
from rest_framework.filters import OrderingFilter
from rest_framework.permissions import IsAuthenticated

from auth_app.api.permissions import IsCustomerUserOrReadOnly
from reviews_app.api.permissions import IsReviewerOrReadOnly
from reviews_app.api.serializers import (
    ReviewSerializer,
    ReviewUpdateSerializer,
)
from reviews_app.models import Review

MAX_ID = 2 ** 63 - 1


def parse_id(params, name):
    """Returns a query param as valid ID, None if empty or invalid."""
    try:
        value = int(params.get(name, ""))
    except ValueError:
        return None
    return value if 0 < value <= MAX_ID else None


class ReviewListView(generics.ListCreateAPIView):
    """Lists reviews with filters; customers can write reviews."""

    serializer_class = ReviewSerializer
    permission_classes = [IsAuthenticated, IsCustomerUserOrReadOnly]
    filter_backends = [OrderingFilter]
    ordering_fields = ["updated_at", "rating"]
    ordering = ["-updated_at"]

    def get_queryset(self):
        """Reviews filtered by business user and reviewer."""
        params = self.request.query_params
        filters = {
            "business_user_id": parse_id(params, "business_user_id"),
            "reviewer_id": parse_id(params, "reviewer_id"),
        }
        active = {k: v for k, v in filters.items() if v is not None}
        return Review.objects.filter(**active)

    def perform_create(self, serializer):
        """Saves the review; a duplicate becomes a 400 error."""
        try:
            with transaction.atomic():
                serializer.save(reviewer=self.request.user)
        except IntegrityError:
            raise ValidationError({"business_user": [
                "You have already reviewed this business user."
            ]})


class ReviewSingleView(generics.UpdateAPIView, generics.DestroyAPIView):
    """Lets the author edit rating/description or delete the review."""

    queryset = Review.objects.all()
    serializer_class = ReviewUpdateSerializer
    permission_classes = [IsAuthenticated, IsReviewerOrReadOnly]
    http_method_names = ["patch", "delete"]
