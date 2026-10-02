from decimal import Decimal

from django.db import transaction
from rest_framework import serializers

from offers_app.models import Offer, OfferDetail

MAX_INT = 2_147_483_647  # largest value of a database integer column
REQUIRED_OFFER_TYPES = {
    OfferDetail.BASIC, OfferDetail.STANDARD, OfferDetail.PREMIUM,
}


class OfferDetailSerializer(serializers.ModelSerializer):
    """Full data of a single offer package; also used for writing."""

    revisions = serializers.IntegerField(min_value=-1, max_value=MAX_INT)
    delivery_time_in_days = serializers.IntegerField(
        min_value=1, max_value=MAX_INT
    )
    price = serializers.DecimalField(
        max_digits=10, decimal_places=2, min_value=Decimal("0")
    )
    features = serializers.ListField(
        child=serializers.CharField(max_length=255), allow_empty=False
    )

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
        """Relative URL of the package detail endpoint."""
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
        """Basic name data of the offer creator."""
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


class OfferWriteSerializer(serializers.ModelSerializer):
    """Creates an offer with its three packages or updates parts of it."""

    details = OfferDetailSerializer(many=True)

    class Meta:
        model = Offer
        fields = ["id", "title", "image", "description", "details"]

    def validate_details(self, details):
        """Requires unique offer types; all three on create."""
        types = [detail.get("offer_type") for detail in details]
        if None in types or len(set(types)) != len(types):
            raise serializers.ValidationError(
                "Each detail needs a unique offer_type."
            )
        if self.instance is None and set(types) != REQUIRED_OFFER_TYPES:
            raise serializers.ValidationError(
                "An offer needs exactly one basic, standard and "
                "premium detail."
            )
        return details

    @transaction.atomic
    def create(self, validated_data):
        """Creates the offer together with its packages."""
        details = validated_data.pop("details")
        offer = Offer.objects.create(**validated_data)
        OfferDetail.objects.bulk_create(
            OfferDetail(offer=offer, **detail) for detail in details
        )
        return offer

    @transaction.atomic
    def update(self, instance, validated_data):
        """Updates the offer and the packages matched by offer_type."""
        details = validated_data.pop("details", [])
        instance = super().update(instance, validated_data)
        for data in details:
            detail = instance.details.get(offer_type=data["offer_type"])
            for attr, value in data.items():
                setattr(detail, attr, value)
            detail.save()
        return instance
