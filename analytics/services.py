from django.utils import timezone

from analytics import exceptions
from analytics.models import Supervision, ActivityStatistics, Failure
from layouts.models import Activity


class FailureService:
    @staticmethod
    def create_failure(activity_statistics: ActivityStatistics) -> Failure:
        failure = Failure.objects.create()

        activity_statistics.failure = failure
        activity_statistics.save(update_fields=["failure"])

        activity_statistics.supervision.validity = False
        activity_statistics.supervision.save(update_fields=["validity"])

        return failure

    @staticmethod
    def finish_failure(activity_statistics: ActivityStatistics) -> Failure:
        failure = activity_statistics.failure

        failure.end_date = timezone.now()
        failure.save(update_fields=["end_date"])

        return failure


class ActivityStatisticsService:
    @staticmethod
    def finish_activity(activity_statistics: ActivityStatistics) -> None:
        activity_statistics.end_date = timezone.now()
        activity_statistics.save(update_fields=["end_date"])

    def start_activity(
        self,
        data: dict,
        previous_activity_statistic: ActivityStatistics = None,
        new_activity: Activity = None,
    ) -> ActivityStatistics:
        if previous_activity_statistic:
            if previous_activity_statistic.activity == new_activity:
                raise exceptions.ActivityAlreadyActivatedException()

            failure = previous_activity_statistic.failure
            if failure and not failure.is_finished:
                data["failure"] = previous_activity_statistic.failure

            self.finish_activity(previous_activity_statistic)
        return ActivityStatistics.objects.create(**data)


class SupervisionService:
    @staticmethod
    def finish_supervision(supervision: Supervision):
        last_activity_statistic = supervision.statistics.filter(
            supervision=supervision, end_date__isnull=True
        ).last()

        if last_activity_statistic:
            ActivityStatisticsService.finish_activity(last_activity_statistic)

            failure = last_activity_statistic.failure
            if failure and not failure.is_finished:
                FailureService.finish_failure(failure)

        supervision.end_date = timezone.now()
        supervision.save(update_fields=["end_date"])
