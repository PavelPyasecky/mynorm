from django.contrib.gis.db import models
from django.utils import timezone

from analytics.utils import get_yandex_map_link
from core import model_mixins
from core.model_mixins import CreatedUpdatedMixin, StartEndDateMixin, VerifiedMixin, PlannedStartEndTimeMixin
from core.models import Organization
from core.utils import timedelta_to_str, time_difference
from layouts.models import Activity
from django.utils.translation import gettext_lazy as _


class Supervision(CreatedUpdatedMixin, StartEndDateMixin, VerifiedMixin, PlannedStartEndTimeMixin):
    worker = models.ForeignKey(
        "users.User",
        verbose_name=_("worker"),
        on_delete=models.CASCADE,
        related_name="worker_supervisions",
    )
    organization = models.ForeignKey(
        Organization,
        verbose_name=_("organization"),
        on_delete=models.CASCADE,
        related_name="organization_supervisions",
    )
    user = models.ForeignKey(
        "users.User",
        verbose_name=_("supervisor"),
        on_delete=models.CASCADE,
        related_name="user_supervisions",
    )
    validity = models.BooleanField(verbose_name=_("validity"), default=True)

    class Meta:
        verbose_name = _("Supervision")
        verbose_name_plural = _("Supervisions")

    def __str__(self):
        return _("Supervision ") + f"{self.pk}"

    @property
    def delta(self):
        if self.end_date and self.start_date:
            return timedelta_to_str(self.end_date - self.start_date)

        return "--:--"

    delta.fget.short_description = _("Duration")

    @property
    def planned_delta(self):
        if self.planned_end_time and self.planned_start_time:
            return timedelta_to_str(time_difference(self.planned_start_time, self.planned_end_time))

        return "--:--:--"

    planned_delta.fget.short_description = _("Planned duration")


class SupervisionComment(CreatedUpdatedMixin):
    text = models.TextField(
        verbose_name=_("text"),
    )
    supervision = models.ForeignKey(
        Supervision,
        verbose_name=_("supervision"),
        on_delete=models.CASCADE,
        related_name="comments",
    )

    def __str__(self):
        return _("Comment") + " №" + str(self.pk)

    class Meta:
        verbose_name = _("Comment")
        verbose_name_plural = _("Comments")


class ActivityStatistics(CreatedUpdatedMixin, StartEndDateMixin, VerifiedMixin):
    activity = models.ForeignKey(
        Activity,
        verbose_name=_("activity"),
        on_delete=models.CASCADE,
        related_name="statistics",
    )
    supervision = models.ForeignKey(
        Supervision,
        verbose_name=_("supervision"),
        on_delete=models.CASCADE,
        related_name="statistics",
    )
    failure = models.ForeignKey(
        "Failure",
        verbose_name=_("failure"),
        null=True,
        on_delete=models.CASCADE,
        related_name="statistics",
    )

    class Meta:
        verbose_name = _("Activity statistics")
        verbose_name_plural = _("Activity statistics")

    def __str__(self):
        return _("Statistics for ") + f"{self.activity.name}"

    @property
    def delta(self):
        if self.end_date and self.start_date:
            return timedelta_to_str(self.end_date - self.start_date)

        return "--:--"

    delta.fget.short_description = _("Duration")


class Comment(CreatedUpdatedMixin):
    text = models.TextField(
        verbose_name=_("text"),
    )
    activity_statistics = models.ForeignKey(
        ActivityStatistics,
        verbose_name=_("activity statistics"),
        on_delete=models.CASCADE,
        related_name="comments",
    )
    coordinates = models.PointField(verbose_name=_("coordinates"), null=True, blank=True)

    @property
    def latitude(self):
        return self.coordinates.y if self.coordinates else None

    @property
    def longitude(self):
        return self.coordinates.x if self.coordinates else None

    @property
    def map_url(self):
        if self.coordinates:
            return get_yandex_map_link(self.latitude, self.longitude)

        return None

    def __str__(self):
        return _("Comment") + " №" + str(self.pk)

    class Meta:
        verbose_name = _("Comment")
        verbose_name_plural = _("Comments")


class CommentImage(CreatedUpdatedMixin):
    image = models.ImageField(verbose_name=_("image"), upload_to="images/")
    comment = models.ForeignKey(
        Comment,
        verbose_name=_("comment"),
        on_delete=models.CASCADE,
        related_name="images",
    )

    class Meta:
        verbose_name = _("Comment Image")
        verbose_name_plural = _("Comment Images")


class CommentFiles(CreatedUpdatedMixin):
    file = models.FileField(verbose_name=_("file"), upload_to="files/")
    comment = models.ForeignKey(
        Comment,
        verbose_name=_("comment"),
        on_delete=models.CASCADE,
        related_name="files",
    )

    class Meta:
        verbose_name = _("Comment File")
        verbose_name_plural = _("Comment Files")


class Failure(model_mixins.StartEndDateMixin):
    pass

    class Meta:
        verbose_name = _("Failure")
        verbose_name_plural = _("Failures")

    @property
    def is_finished(self):
        return self.end_date

    @property
    def delta(self):
        if self.end_date and self.start_date:
            return timedelta_to_str(self.end_date - self.start_date)

        elif self.start_date:
            return timedelta_to_str(timezone.now() - self.start_date)

        return "--:--"

    delta.fget.short_description = _("Duration")

    def __str__(self):
        return _(f"Failure") + f" #{self.id} - {self.delta}"
