from django.contrib.auth.models import User
from django.db import models

from offers_app.models import OfferDetail


class Order(models.Model):
    """A purchased offer package, stored as a snapshot of its data."""

    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    STATUS_CHOICES = [
        (IN_PROGRESS, "In progress"),
        (COMPLETED, "Completed"),
        (CANCELLED, "Cancelled"),
    ]

    customer_user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="orders"
    )
    business_user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="received_orders"
    )
    title = models.CharField(max_length=255)
    revisions = models.IntegerField()
    delivery_time_in_days = models.IntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    features = models.JSONField(default=list)
    offer_type = models.CharField(
        max_length=10, choices=OfferDetail.OFFER_TYPE_CHOICES
    )
    status = models.CharField(
        max_length=20, choices=STATUS_CHOICES, default=IN_PROGRESS
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "order"
        verbose_name_plural = "orders"
        ordering = ["-created_at"]

    def __str__(self):
        """Order title with status."""
        return f"{self.title} ({self.status})"
