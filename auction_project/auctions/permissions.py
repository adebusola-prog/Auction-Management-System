from rest_framework.permissions import BasePermission

class IsStaffuserOnlyPermission(BasePermission):
    """
    Custom permission to allow only superusers to access the view.
    """

    def has_permission(self, request, view):
        return request.user.is_staff