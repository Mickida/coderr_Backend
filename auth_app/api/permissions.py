from rest_framework.permissions import SAFE_METHODS, BasePermission

from auth_app.models import Profile


class IsProfileOwnerOrReadOnly(BasePermission):
    """Allows reading any profile but editing only your own."""

    def has_object_permission(self, request, view, obj):
        if request.method in SAFE_METHODS:
            return True
        return obj.user_id == request.user.id


def has_profile_type(user, profile_type):
    """True if the user has a profile of the given type."""
    profile = getattr(user, "profile", None)
    return profile is not None and profile.type == profile_type


class IsBusinessUserOrReadOnly(BasePermission):
    """Allows reading to everyone, writing only to business users."""

    message = "Only business users can perform this action."

    def has_permission(self, request, view):
        if request.method in SAFE_METHODS:
            return True
        return has_profile_type(request.user, Profile.BUSINESS)


class IsCustomerUserOrReadOnly(BasePermission):
    """Allows reading to everyone, writing only to customer users."""

    message = "Only customer users can perform this action."

    def has_permission(self, request, view):
        if request.method in SAFE_METHODS:
            return True
        return has_profile_type(request.user, Profile.CUSTOMER)
