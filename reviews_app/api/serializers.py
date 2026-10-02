from django.contrib.auth.models import User
from rest_framework import serializers

from auth_app.models import Profile
from reviews_app.models import Review


class ReviewSerializer(serializers.ModelSerializer):
    """Review data; on create, one review per business user and author."""

    business_user = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.filter(profile__type=Profile.BUSINESS)
    )
    rating = serializers.IntegerField(min_value=1, max_value=5)

    class Meta:
        model = Review
        fields = [
            "id", "business_user", "reviewer", "rating", "description",
            "created_at", "updated_at",
        ]
        read_only_fields = ["reviewer", "created_at", "updated_at"]

    def validate_business_user(self, value):
        reviewer = self.context["request"].user
        if Review.objects.filter(business_user=value,
                                 reviewer=reviewer).exists():
            raise serializers.ValidationError(
                "You have already reviewed this business user."
            )
        return value


class ReviewUpdateSerializer(ReviewSerializer):
    """Review data where only rating and description are editable."""

    business_user = serializers.PrimaryKeyRelatedField(read_only=True)
