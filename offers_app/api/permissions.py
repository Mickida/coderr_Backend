from rest_framework.permissions import SAFE_METHODS, BasePermission


class IsOfferOwnerOrReadOnly(BasePermission):
    """Allows reading any offer but changing only your own."""

    def has_object_permission(self, request, view, obj):
        if request.method in SAFE_METHODS:
            return True
        return obj.user_id == request.user.id
