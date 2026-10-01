from django.contrib.auth.models import User
from django.db import models


class Offer(models.Model):
    """A service offered by a business user, sold in three packages."""

    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="offers"
    )
    title = models.CharField(max_length=255)
    image = models.ImageField(upload_to="offers/", blank=True, null=True)
    description = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "offer"
        verbose_name_plural = "offers"
        ordering = ["-updated_at"]

    def __str__(self):
        return self.title


class OfferDetail(models.Model):
    """One package of an offer; revisions == -1 means unlimited."""

    BASIC = "basic"
    STANDARD = "standard"
    PREMIUM = "premium"
    OFFER_TYPE_CHOICES = [
        (BASIC, "Basic"), (STANDARD, "Standard"), (PREMIUM, "Premium"),
    ]

    offer = models.ForeignKey(
        Offer, on_delete=models.CASCADE, related_name="details"
    )
    title = models.CharField(max_length=255)
    revisions = models.IntegerField()
    delivery_time_in_days = models.IntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    features = models.JSONField(default=list)
    offer_type = models.CharField(max_length=10, choices=OFFER_TYPE_CHOICES)

    class Meta:
        verbose_name = "offer detail"
        verbose_name_plural = "offer details"
        ordering = ["id"]
        constraints = [
            models.UniqueConstraint(
                fields=["offer", "offer_type"],
                name="unique_offer_type_per_offer",
            ),
        ]

    def __str__(self):
        return f"{self.offer.title} ({self.offer_type})"
