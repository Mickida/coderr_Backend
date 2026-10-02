from rest_framework.permissions import SAFE_METHODS, BasePermission


class IsReviewerOrReadOnly(BasePermission):
    """Allows changing or deleting a review only by its author."""

    def has_object_permission(self, request, view, obj):
        if request.method in SAFE_METHODS:
            return True
        return obj.reviewer_id == request.user.id
