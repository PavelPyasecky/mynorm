from rest_framework.permissions import BasePermission, IsAuthenticated, DjangoObjectPermissions

from users.signals import ConstantGroups


class IsSupervisor(IsAuthenticated, BasePermission):
    """
    Custom permission to only allow supervisors get it.
    """

    def has_permission(self, request, view):
        return request.user.is_staff and super().has_permission(request, view)


class IsSupervisorGroup(IsAuthenticated, BasePermission):
    """
    Custom permission to only allow users with SUPERVISOR group.
    """

    def has_permission(self, request, view):
        # Check if user is authenticated first
        if not super().has_permission(request, view):
            return False
        
        return request.user.groups.filter(name=ConstantGroups.SUPERVISOR).exists()


class IsWorkerGroup(IsAuthenticated, BasePermission):
    """
    Custom permission to only allow users with WORKER group.
    """

    def has_permission(self, request, view):
        # Check if user is authenticated first
        if not super().has_permission(request, view):
            return False

        return request.user.groups.filter(name=ConstantGroups.WORKER).exists()

class CustomDjangoObjectPermissions(DjangoObjectPermissions):
    perms_map = {
        'GET': ['%(app_label)s.view_%(model_name)s'],
        'OPTIONS': [],
        'HEAD': [],
        'POST': ['%(app_label)s.add_%(model_name)s'],
        'PUT': ['%(app_label)s.change_%(model_name)s'],
        'PATCH': ['%(app_label)s.change_%(model_name)s'],
        'DELETE': ['%(app_label)s.delete_%(model_name)s'],
    }
