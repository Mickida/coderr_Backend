from django.db.models import Min
from rest_framework import generics
from rest_framework.exceptions import ValidationError
from rest_framework.filters import OrderingFilter, SearchFilter
from rest_framework.permissions import IsAuthenticated

from auth_app.api.permissions import IsBusinessUserOrReadOnly
from offers_app.api.pagination import OfferPagination
from offers_app.api.permissions import IsOfferOwnerOrReadOnly
from offers_app.api.serializers import (
    OfferDetailSerializer,
    OfferListSerializer,
    OfferRetrieveSerializer,
    OfferWriteSerializer,
)
from offers_app.models import Offer, OfferDetail


def annotated_offers():
    """Offers with the lowest package price and fastest delivery."""
    return (
        Offer.objects.select_related("user")
        .prefetch_related("details")
        .annotate(
            min_price=Min("details__price"),
            min_delivery_time=Min("details__delivery_time_in_days"),
        )
    )


def parse_number(params, name, cast):
    """Returns a query param as number, None if empty, 400 if invalid."""
    value = params.get(name, "").strip()
    if not value:
        return None
    try:
        return cast(value)
    except ValueError:
        raise ValidationError({name: "A valid number is required."})


class OfferListView(generics.ListCreateAPIView):
    """Public offer list; business users can create offers."""

    permission_classes = [IsBusinessUserOrReadOnly]
    pagination_class = OfferPagination
    filter_backends = [SearchFilter, OrderingFilter]
    search_fields = ["title", "description"]
    ordering_fields = ["updated_at", "min_price"]
    ordering = ["-updated_at"]

    def get_serializer_class(self):
        """Write serializer for POST, list serializer otherwise."""
        if self.request.method == "POST":
            return OfferWriteSerializer
        return OfferListSerializer

    def get_queryset(self):
        """Offers filtered by creator, minimum price and delivery time."""
        params = self.request.query_params
        filters = {
            "user_id": parse_number(params, "creator_id", int),
            "min_price__gte": parse_number(params, "min_price", float),
            "min_delivery_time__lte": parse_number(
                params, "max_delivery_time", int
            ),
        }
        active = {k: v for k, v in filters.items() if v is not None}
        return annotated_offers().filter(**active)

    def perform_create(self, serializer):
        """Saves the offer for the requesting business user."""
        serializer.save(user=self.request.user)


class OfferSingleView(generics.RetrieveUpdateDestroyAPIView):
    """Shows an offer; only its creator may update or delete it."""

    permission_classes = [IsAuthenticated, IsOfferOwnerOrReadOnly]
    http_method_names = ["get", "patch", "delete"]

    def get_queryset(self):
        """Offers with lowest price and fastest delivery annotated."""
        return annotated_offers()

    def get_serializer_class(self):
        """Detail serializer for GET, write serializer otherwise."""
        if self.request.method == "GET":
            return OfferRetrieveSerializer
        return OfferWriteSerializer


class OfferDetailView(generics.RetrieveAPIView):
    """Shows a single offer package to authenticated users."""

    queryset = OfferDetail.objects.all()
    serializer_class = OfferDetailSerializer
    permission_classes = [IsAuthenticated]
