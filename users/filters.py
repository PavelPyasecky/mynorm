from rest_framework.filters import BaseFilterBackend
from django.contrib.auth.models import Group
from django.db.models import Q

from users.signals import ConstantGroups


class UserFilter(BaseFilterBackend):
    """
    Filter backend for User model.
    Supports filtering by role (supervisor, worker, administrator).
    
    Query parameters:
    - role: 'supervisor', 'worker', 'administrator' (or 'admin')
    - only_workers: 'true' (backward compatibility)
    - only_supervisors: 'true' (backward compatibility)
    """
    
    # Mapping of role values to group names
    ROLE_TO_GROUP = {
        "supervisor": ConstantGroups.SUPERVISOR,
        "worker": ConstantGroups.WORKER,
    }
    
    # Backward compatibility parameter mapping
    LEGACY_PARAM_TO_GROUP = {
        "only_workers": ConstantGroups.WORKER,
        "only_supervisors": ConstantGroups.SUPERVISOR,
    }
    
    def filter_queryset(self, request, queryset, view):
        """Filter queryset based on role parameters."""
        role = self._get_role_from_params(request)
        
        if not role:
            return queryset
        
        if role in ("administrator", "admin"):
            return self._filter_administrators(queryset)
        
        if role in self.ROLE_TO_GROUP:
            return self._filter_by_group(queryset, self.ROLE_TO_GROUP[role])
        
        return queryset
    
    def _get_role_from_params(self, request):
        """Extract role from query parameters, checking new parameter first, then legacy."""
        role = request.query_params.get("role", "").lower()
        if role:
            return role
        
        # Backward compatibility: check legacy parameters
        for param, group_name in self.LEGACY_PARAM_TO_GROUP.items():
            if request.query_params.get(param) == "true":
                # Map legacy param to role value
                return group_name.lower()
        
        return None
    
    def _filter_by_group(self, queryset, group_name):
        """Filter users by group membership."""
        try:
            group = Group.objects.get(name=group_name)
            return queryset.filter(groups=group).distinct()
        except Group.DoesNotExist:
            return queryset.none()
    
    def _filter_administrators(self, queryset):
        """Filter users who are administrators (Admin group, staff, or superuser)."""
        query = Q(is_staff=True) | Q(is_superuser=True)
        
        try:
            admin_group = Group.objects.get(name=ConstantGroups.ADMIN)
            query |= Q(groups=admin_group)
        except Group.DoesNotExist:
            pass
        
        return queryset.filter(query).distinct()
