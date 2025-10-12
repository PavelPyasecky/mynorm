from django.db import models
from ordered_model.models import OrderedModel

from core.model_mixins import CreatedUpdatedMixin, StartEndDateMixin, PlannedStartEndTimeMixin
from core.models import Organization, Classifier
from core.utils import timedelta_to_str, time_difference
from gallery.models import ImageGallery
from django.utils.translation import gettext_lazy as _


class Layout(OrderedModel, CreatedUpdatedMixin):
    name = models.CharField(_("name"), null=True, max_length=255)
    organization = models.ForeignKey(
        Organization,
        verbose_name=_("organization"),
        on_delete=models.CASCADE,
        related_name="layouts",
    )
    classifier = models.OneToOneField(
        Classifier,
        verbose_name=_("classifier"),
        on_delete=models.CASCADE,
        related_name="layout",
    )

    class Meta(OrderedModel.Meta):
        verbose_name = _("Layout")
        verbose_name_plural = _("Layouts")

    def __str__(self):
        return self.name or _("Layout #") + self.id


class ActivityGroup(OrderedModel, CreatedUpdatedMixin):
    class ColumnNumberChoice(models.IntegerChoices):
        ONE = 1, _("Placement in the first column")
        TWO = 2, _("Placement in the second column")
        THREE = 3, _("Placement in the third column")

    name = models.CharField(max_length=255)
    layout = models.ForeignKey(
        Layout,
        verbose_name=_("layout"),
        on_delete=models.CASCADE,
        related_name="activity_groups",
    )
    image = models.ForeignKey(
        ImageGallery,
        verbose_name=_("image"),
        on_delete=models.CASCADE,
        null=True,
        related_name="activity_group",
    )
    column_number = models.PositiveSmallIntegerField(
        choices=ColumnNumberChoice.choices, default=ColumnNumberChoice.ONE
    )

    order_with_respect_to = "layout"

    def __str__(self):
        return self.name

    class Meta(OrderedModel.Meta):
        verbose_name = _("Activity Group")
        verbose_name_plural = _("Activity Groups")
        ordering = ("order",)


class Activity(OrderedModel, CreatedUpdatedMixin, PlannedStartEndTimeMixin):
    name = models.CharField(verbose_name=_("name"), max_length=255)
    activity_group = models.ForeignKey(
        ActivityGroup,
        verbose_name=_("activity group"),
        on_delete=models.CASCADE,
        related_name="activities",
    )

    order_with_respect_to = "activity_group"

    def __str__(self):
        return self.name

    class Meta(OrderedModel.Meta):
        verbose_name = _("Activity")
        verbose_name_plural = _("Activities")

    @property
    def planned_delta(self):
        if self.planned_end_time and self.planned_start_time:
            return timedelta_to_str(time_difference(self.planned_start_time, self.planned_end_time))

        return "--:--:--"

    planned_delta.fget.short_description = _("Planned duration")
