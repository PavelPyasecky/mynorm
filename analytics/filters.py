from datetime import date, datetime

from django.utils import timezone
from rest_framework.filters import BaseFilterBackend

from analytics.models import Supervision
from analytics.utils import parse_date_query_param


class SupervisionDateFilter(BaseFilterBackend):
    """Filter backend for filtering supervisions by start_date within a date range."""

    def filter_queryset(self, request, queryset, view):
        """Filter supervisions where start_date falls within the provided date range."""
        start_date_param = request.query_params.get('start_date')
        end_date_param = request.query_params.get('end_date')
        
        if not start_date_param and not end_date_param:
            return queryset
        
        start_date = parse_date_query_param(start_date_param) if start_date_param else None
        end_date = parse_date_query_param(end_date_param) if end_date_param else None
        
        if start_date_param and not start_date:
            return queryset.none()
        if end_date_param and not end_date:
            return queryset.none()
        
        if start_date:
            query_start_datetime = timezone.make_aware(
                datetime.combine(start_date, datetime.min.time())
            )
            queryset = queryset.filter(start_date__gte=query_start_datetime)
        
        if end_date:
            query_end_datetime = timezone.make_aware(
                datetime.combine(end_date, datetime.max.time())
            )
            queryset = queryset.filter(start_date__lte=query_end_datetime)
        
        return queryset

