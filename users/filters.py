from rest_framework.filters import BaseFilterBackend


class UserFilter(BaseFilterBackend):
    def filter_queryset(self, request, queryset, view):
        if request.query_params.get('only_workers') == 'true':
            return queryset.filter(is_staff=False)
        if request.query_params.get('only_supervisors') == 'true':
            return queryset.filter(is_staff=True)
        return queryset