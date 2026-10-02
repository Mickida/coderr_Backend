from rest_framework import serializers

MAX_IMAGE_SIZE = 5 * 1024 * 1024  # 5 MB


def validate_image_size(image):
    """Rejects uploaded images larger than the allowed size."""
    if image and image.size > MAX_IMAGE_SIZE:
        raise serializers.ValidationError(
            "The image must not be larger than 5 MB."
        )
    return image
