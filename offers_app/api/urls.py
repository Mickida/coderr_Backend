from django.urls import path

from offers_app.api.views import (
    OfferDetailView,
    OfferListView,
    OfferSingleView,
)

urlpatterns = [
    path("offers/", OfferListView.as_view(), name="offer-list"),
    path("offers/<int:pk>/", OfferSingleView.as_view(),
         name="offer-detail"),
    path("offerdetails/<int:pk>/", OfferDetailView.as_view(),
         name="offerdetail-detail"),
]
