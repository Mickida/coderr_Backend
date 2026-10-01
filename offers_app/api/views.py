from django.db.models import Min
from rest_framework import generics
from rest_framework.exceptions import ValidationError
from rest_framework.filters import OrderingFilter, SearchFilter
from rest_framework.permissions import AllowAny

from offers_app.api.pagination import OfferPagination
from offers_app.api.serializers import (
    OfferDetailSerializer,
    OfferListSerializer,
    OfferRetrieveSerializer,
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


class OfferListView(generics.ListAPIView):
    """Public, paginated offer list with filters, search and ordering."""

    serializer_class = OfferListSerializer
    permission_classes = [AllowAny]
    pagination_class = OfferPagination
    filter_backends = [SearchFilter, OrderingFilter]
    search_fields = ["title", "description"]
    ordering_fields = ["updated_at", "min_price"]
    ordering = ["-updated_at"]

    def get_queryset(self):
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


class OfferSingleView(generics.RetrieveAPIView):
    """Shows a single offer to authenticated users."""

    serializer_class = OfferRetrieveSerializer

    def get_queryset(self):
        return annotated_offers()


class OfferDetailView(generics.RetrieveAPIView):
    """Shows a single offer package to authenticated users."""

    queryset = OfferDetail.objects.all()
    serializer_class = OfferDetailSerializer
