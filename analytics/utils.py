from django.db.models import QuerySet
from django.utils import timezone

from analytics.models import ActivityStatistics, Supervision


def deactivate_activities(activities_statistic: QuerySet[ActivityStatistics]) -> None:
    activities_statistic.update(end_date=timezone.now())


def deactivate_activity(activity_statistic: ActivityStatistics) -> None:
    activity_statistic.end_date = timezone.now()
    activity_statistic.save(update_fields=['end_date'])


def finish_supervision(supervision: Supervision) -> None:
    supervision.end_date = timezone.now()
    supervision.save(update_fields=['end_date'])


def finish_supervision_with_failure(supervision: Supervision) -> None:
    supervision.end_date = timezone.now()
    supervision.valid = False
    supervision.save(update_fields=['end_date', 'valid'])
