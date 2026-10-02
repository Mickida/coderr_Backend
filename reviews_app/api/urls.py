from django.urls import path

from reviews_app.api.views import ReviewListView, ReviewSingleView

urlpatterns = [
    path("reviews/", ReviewListView.as_view(), name="review-list"),
    path("reviews/<int:pk>/", ReviewSingleView.as_view(),
         name="review-detail"),
]
