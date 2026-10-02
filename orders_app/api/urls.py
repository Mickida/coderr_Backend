from django.urls import path

from orders_app.api.views import (
    CompletedOrderCountView,
    OrderCountView,
    OrderListView,
    OrderSingleView,
)

urlpatterns = [
    path("orders/", OrderListView.as_view(), name="order-list"),
    path("orders/<int:pk>/", OrderSingleView.as_view(),
         name="order-detail"),
    path("order-count/<int:business_user_id>/", OrderCountView.as_view(),
         name="order-count"),
    path("completed-order-count/<int:business_user_id>/",
         CompletedOrderCountView.as_view(), name="completed-order-count"),
]
