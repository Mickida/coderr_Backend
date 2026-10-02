from django.contrib import admin

from orders_app.models import Order


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    """Order admin where only the status is editable."""

    list_display = ["id", "title", "customer_user", "business_user",
                    "status", "created_at"]
    list_filter = ["status"]
    readonly_fields = [
        "customer_user", "business_user", "title", "revisions",
        "delivery_time_in_days", "price", "features", "offer_type",
        "created_at", "updated_at",
    ]
