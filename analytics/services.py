from django.utils import timezone

from analytics import exceptions
from analytics.models import (
    Supervision,
    ActivityStatistics,
    Failure,
    Comment,
    CommentFiles
)
from core.model_mixins import VerifiedMixin
from layouts.models import Activity
from users.models import User


class FailureService:
    @staticmethod
    def create_failure(activity_statistics: ActivityStatistics) -> Failure:
        failure = Failure.objects.create()

        activity_statistics.failure = failure
        activity_statistics.save(update_fields=["failure"])

        activity_statistics.supervision.validity = False
        activity_statistics.supervision.save(update_fields=["validity"])

        return failure

    def finish_failure(self, activity_statistics: ActivityStatistics) -> Failure:
        failure = activity_statistics.failure

        if not failure:
            activity_statistics.failure = failure
            activity_statistics.save(update_fields=["failure"])

            activity_statistics_with_last_failure = self._get_analytics_with_last_failure(
                activity_statistics.supervision.pk)

            self._mark_intermediate_activity_statistics_as_failed(
                activity_statistics_with_last_failure, activity_statistics, failure)

        failure.end_date = timezone.now()
        failure.save(update_fields=["end_date"])

        return failure

    @staticmethod
    def _get_analytics_with_last_failure(supervision_id: int) -> ActivityStatistics:
        activity_statistics = ActivityStatistics.objects.filter(
            supervision_id=supervision_id, failure_id__isnull=False).order_by("-id").first()

        if activity_statistics:
            return activity_statistics

        raise exceptions.ActivityAlreadyActivatedException()

    @staticmethod
    def _mark_intermediate_activity_statistics_as_failed(first_analytics: ActivityStatistics,
                                                         last_analytics: ActivityStatistics,
                                                         failure: Failure) -> None:
        ActivityStatistics.objects.filter(
            id__gt=first_analytics, id__lt=last_analytics).update(failure=failure)


class VerifyMixin:
    def _change_verification(self, entity: VerifiedMixin, verify: bool) -> None:
        entity.verified = verify
        entity.verification_date = timezone.now()
        entity.save(update_fields=["verified", "verification_date"])

    def verify(self, entity: VerifiedMixin):
        self._change_verification(entity, True)

    def clear_verification(self, entity: VerifiedMixin):
        self._change_verification(entity, False)


class ActivityStatisticsService(VerifyMixin):
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


class SupervisionService(VerifyMixin):
    @staticmethod
    def finish_supervision(supervision: Supervision):
        last_activity_statistic = supervision.statistics.filter(
            supervision=supervision, end_date__isnull=True
        ).last()

        if last_activity_statistic:
            ActivityStatisticsService.finish_activity(last_activity_statistic)

            failure = last_activity_statistic.failure
            if failure and not failure.is_finished:
                FailureService().finish_failure(last_activity_statistic)

        supervision.end_date = timezone.now()
        supervision.save(update_fields=["end_date"])

    @staticmethod
    def delete_not_verified_supervisions() -> tuple[int,dict[str, int]]:
        deleted_entities_count, deleted_entities_dict = Supervision.objects.filter(verified=False).delete()
        return deleted_entities_count, deleted_entities_dict

    @staticmethod
    def get_user_last_active_supervision(user: User) -> Supervision:
        return Supervision.objects.filter(user=user, end_date__isnull=True).order_by("id").last()


class CommentService:
    @staticmethod
    def create_comment(
        activity_statistics_id: int,
        user: User,
        text: str = None,
        coordinates: dict = None,
        files: list = None
    ) -> Comment:
        if not (text or files):
            return None

        comment = Comment.objects.create(
            activity_statistics_id=activity_statistics_id,
            text=text,
            coordinates=coordinates,
            created_by=user,
            updated_by=user,
        )

        if files:
            file_objects = [
                CommentFiles(comment=comment, file=file) for file in files
            ]
            CommentFiles.objects.bulk_create(file_objects)

        return comment
