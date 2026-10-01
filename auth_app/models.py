from django.contrib.auth.models import User
from django.db import models


class Profile(models.Model):
    """Platform-specific data attached to every user (business or customer)."""

    BUSINESS = "business"
    CUSTOMER = "customer"
    TYPE_CHOICES = [(BUSINESS, "Business"), (CUSTOMER, "Customer")]

    user = models.OneToOneField(
        User, on_delete=models.CASCADE, related_name="profile"
    )
    type = models.CharField(max_length=10, choices=TYPE_CHOICES)
    file = models.ImageField(upload_to="profiles/", blank=True, null=True)
    location = models.CharField(max_length=255, blank=True, default="")
    tel = models.CharField(max_length=50, blank=True, default="")
    description = models.TextField(blank=True, default="")
    working_hours = models.CharField(max_length=255, blank=True, default="")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "profile"
        verbose_name_plural = "profiles"
        ordering = ["user__username"]

    def __str__(self):
        return f"{self.user.username} ({self.type})"
