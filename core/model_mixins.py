from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _


class CreatedUpdatedDateMixin(models.Model):
    created_date = models.DateTimeField(
        verbose_name=_("created_date"), default=timezone.now
    )
    updated_date = models.DateTimeField(
        verbose_name=_("updated_date"), default=timezone.now
    )

    class Meta:
        abstract = True


class CreatedUpdatedByMixin(models.Model):
    created_by = models.ForeignKey(
        "users.User",
        verbose_name=_("created by"),
        on_delete=models.SET_NULL,
        related_name="%(class)s_created",
        null=True,
        blank=True,
    )
    updated_by = models.ForeignKey(
        "users.User",
        verbose_name=_("updated by"),
        on_delete=models.SET_NULL,
        related_name="%(class)s_updated",
        null=True,
        blank=True,
    )

    class Meta:
        abstract = True


class CreatedUpdatedMixin(CreatedUpdatedByMixin, CreatedUpdatedDateMixin):
    class Meta:
        abstract = True


class StartEndDateMixin(models.Model):
    start_date = models.DateTimeField(
        verbose_name=_("start date"), default=timezone.now
    )
    end_date = models.DateTimeField(
        verbose_name=_("end date"), null=True, blank=True
    )

    class Meta:
        abstract = True


class VerifiedMixin(models.Model):
    verified = models.BooleanField(
        verbose_name=_("verified"), default=False
    )
    verification_date = models.DateTimeField(
        verbose_name=_("verification_date"), null=True, blank=True
    )

    class Meta:
        abstract = True
