from rest_framework.permissions import BasePermission


class IsOrderBusinessUserOrStaffDelete(BasePermission):
    """Only staff may delete; only the order's business user may edit."""

    def has_permission(self, request, view):
        if request.method == "DELETE":
            return request.user.is_staff
        return True

    def has_object_permission(self, request, view, obj):
        if request.method == "DELETE":
            return True
        return obj.business_user_id == request.user.id
