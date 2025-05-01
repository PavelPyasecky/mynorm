from rest_framework.permissions import BasePermission, IsAuthenticated


class IsSupervisor(IsAuthenticated, BasePermission):
    """
    Custom permission to only allow supervisors get it.
    """

    def has_permission(self, request, view):
        return request.user.is_staff and super().has_permission(request, view)
