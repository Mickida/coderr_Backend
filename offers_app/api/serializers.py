from rest_framework import serializers

from offers_app.models import Offer, OfferDetail


class OfferDetailSerializer(serializers.ModelSerializer):
    """Full data of a single offer package."""

    class Meta:
        model = OfferDetail
        fields = [
            "id", "title", "revisions", "delivery_time_in_days", "price",
            "features", "offer_type",
        ]


class OfferDetailLinkSerializer(serializers.ModelSerializer):
    """Package reference in the offer list: id and relative URL."""

    url = serializers.SerializerMethodField()

    class Meta:
        model = OfferDetail
        fields = ["id", "url"]

    def get_url(self, obj):
        return f"/offerdetails/{obj.id}/"


class OfferDetailHyperlinkSerializer(serializers.ModelSerializer):
    """Package reference on a single offer: id and absolute URL."""

    url = serializers.HyperlinkedIdentityField(
        view_name="offerdetail-detail"
    )

    class Meta:
        model = OfferDetail
        fields = ["id", "url"]


class OfferListSerializer(serializers.ModelSerializer):
    """Offer as shown in the paginated list, incl. creator names."""

    details = OfferDetailLinkSerializer(many=True, read_only=True)
    min_price = serializers.DecimalField(
        max_digits=10, decimal_places=2, read_only=True
    )
    min_delivery_time = serializers.IntegerField(read_only=True)
    user_details = serializers.SerializerMethodField()

    class Meta:
        model = Offer
        fields = [
            "id", "user", "title", "image", "description", "created_at",
            "updated_at", "details", "min_price", "min_delivery_time",
            "user_details",
        ]

    def get_user_details(self, obj):
        return {
            "first_name": obj.user.first_name,
            "last_name": obj.user.last_name,
            "username": obj.user.username,
        }


class OfferRetrieveSerializer(OfferListSerializer):
    """Single offer with absolute package URLs, without creator names."""

    details = OfferDetailHyperlinkSerializer(many=True, read_only=True)

    class Meta(OfferListSerializer.Meta):
        fields = [
            "id", "user", "title", "image", "description", "created_at",
            "updated_at", "details", "min_price", "min_delivery_time",
        ]
