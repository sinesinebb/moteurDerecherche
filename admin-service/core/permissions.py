from rest_framework import permissions

class IsAdminUser(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user and hasattr(request.user, 'is_admin') and request.user.is_admin