from abc import ABC, abstractmethod
from datetime import date, datetime
from typing import Optional

from django.db.models import Q, QuerySet
from django.utils import timezone
from rest_framework.filters import BaseFilterBackend

from analytics.models import Supervision
from analytics.utils import dates_are_same_day, parse_date_query_param


class DateRangeFilterStrategy(ABC):
    """Abstract base class for date filtering strategies."""

    @abstractmethod
    def filter(self, queryset: QuerySet[Supervision], start_date: date, end_date: date) -> QuerySet[Supervision]:
        """Apply filtering logic to the queryset."""
        pass


class SameDayOverlapStrategy(DateRangeFilterStrategy):
    """Strategy for filtering supervisions active on a specific date."""

    def filter(self, queryset: QuerySet[Supervision], start_date: date, end_date: date) -> QuerySet[Supervision]:
        """Filter supervisions that were active on the specified date."""
        query_date = start_date
        
        query_datetime_start = timezone.make_aware(
            datetime.combine(query_date, datetime.min.time())
        )
        query_datetime_end = timezone.make_aware(
            datetime.combine(query_date, datetime.max.time())
        )
        
        return queryset.filter(
            start_date__lte=query_datetime_end
        ).filter(
            Q(end_date__gte=query_datetime_start) | Q(end_date__isnull=True)
        )


class DateRangeStrategy(DateRangeFilterStrategy):
    """Strategy for filtering supervisions within a date range."""

    def filter(self, queryset: QuerySet[Supervision], start_date: date, end_date: date) -> QuerySet[Supervision]:
        """Filter supervisions where both start_date and end_date fall within the query range."""
        query_start_datetime = timezone.make_aware(
            datetime.combine(start_date, datetime.min.time())
        )
        query_end_datetime = timezone.make_aware(
            datetime.combine(end_date, datetime.max.time())
        )
        
        return queryset.filter(
            start_date__gte=query_start_datetime,
        ).filter(
            Q(end_date__lte=query_end_datetime) | Q(end_date__isnull=True)
        )


class SupervisionDateFilter(BaseFilterBackend):
    """Filter backend for filtering supervisions by date range."""

    def filter_queryset(self, request, queryset, view):
        """Apply date filtering to the queryset based on query parameters."""
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
        
        if start_date and not end_date:
            end_date = start_date
        elif end_date and not start_date:
            start_date = end_date
        
        if dates_are_same_day(start_date, end_date):
            strategy: DateRangeFilterStrategy = SameDayOverlapStrategy()
        else:
            strategy: DateRangeFilterStrategy = DateRangeStrategy()
        
        return strategy.filter(queryset, start_date, end_date)

