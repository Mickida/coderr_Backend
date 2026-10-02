from rest_framework import serializers

from orders_app.models import Order


class OrderSerializer(serializers.ModelSerializer):
    """Order output; only 'status' may be changed, other keys are 400."""

    class Meta:
        model = Order
        fields = [
            "id", "customer_user", "business_user", "title", "revisions",
            "delivery_time_in_days", "price", "features", "offer_type",
            "status", "created_at", "updated_at",
        ]
        read_only_fields = [
            "id", "customer_user", "business_user", "title", "revisions",
            "delivery_time_in_days", "price", "features", "offer_type",
            "created_at", "updated_at",
        ]

    def validate(self, attrs):
        """Allows only the status field and requires it."""
        unknown = set(self.initial_data) - {"status"}
        if unknown:
            raise serializers.ValidationError(
                {field: "This field cannot be changed." for field in unknown}
            )
        if "status" not in attrs:
            raise serializers.ValidationError(
                {"status": "This field is required."}
            )
        return attrs


class OfferDetailIdSerializer(serializers.Serializer):
    """Validates the package ID a customer wants to order."""

    offer_detail_id = serializers.IntegerField()
