from django.urls import path

from orders_app.api.views import OrderListView, OrderSingleView

urlpatterns = [
    path("orders/", OrderListView.as_view(), name="order-list"),
    path("orders/<int:pk>/", OrderSingleView.as_view(),
         name="order-detail"),
]
