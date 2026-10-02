from django.contrib.auth.models import User
from django.db.models import Q
from django.shortcuts import get_object_or_404
from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from auth_app.api.permissions import IsCustomerUserOrReadOnly
from auth_app.models import Profile
from offers_app.models import OfferDetail
from orders_app.api.permissions import IsOrderBusinessUserOrStaffDelete
from orders_app.api.serializers import (
    OfferDetailIdSerializer,
    OrderSerializer,
)
from orders_app.models import Order


def create_order_from_detail(detail, customer):
    """Copies the package data into a new order for the customer."""
    return Order.objects.create(
        customer_user=customer,
        business_user=detail.offer.user,
        title=detail.title,
        revisions=detail.revisions,
        delivery_time_in_days=detail.delivery_time_in_days,
        price=detail.price,
        features=detail.features,
        offer_type=detail.offer_type,
    )


class OrderListView(generics.ListCreateAPIView):
    """Lists the user's orders; customers can order an offer package."""

    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated, IsCustomerUserOrReadOnly]

    def get_queryset(self):
        user = self.request.user
        return Order.objects.filter(
            Q(customer_user=user) | Q(business_user=user)
        )

    def create(self, request, *args, **kwargs):
        serializer = OfferDetailIdSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        detail = get_object_or_404(
            OfferDetail.objects.select_related("offer"),
            pk=serializer.validated_data["offer_detail_id"],
        )
        order = create_order_from_detail(detail, request.user)
        return Response(
            OrderSerializer(order).data, status=status.HTTP_201_CREATED
        )


class OrderSingleView(generics.UpdateAPIView, generics.DestroyAPIView):
    """Business user updates the status; only staff may delete."""

    queryset = Order.objects.all()
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated, IsOrderBusinessUserOrStaffDelete]
    http_method_names = ["patch", "delete"]


def count_orders(business_user_id, order_status):
    """Counts a business user's orders in a status; 404 if no such user."""
    business_user = get_object_or_404(
        User, pk=business_user_id, profile__type=Profile.BUSINESS
    )
    return Order.objects.filter(
        business_user=business_user, status=order_status
    ).count()


class OrderCountView(APIView):
    """Returns the number of a business user's orders in progress."""

    permission_classes = [IsAuthenticated]

    def get(self, request, business_user_id):
        count = count_orders(business_user_id, Order.IN_PROGRESS)
        return Response({"order_count": count})


class CompletedOrderCountView(APIView):
    """Returns the number of a business user's completed orders."""

    permission_classes = [IsAuthenticated]

    def get(self, request, business_user_id):
        count = count_orders(business_user_id, Order.COMPLETED)
        return Response({"completed_order_count": count})
