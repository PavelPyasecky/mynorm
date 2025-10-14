from django.contrib.auth.models import AbstractUser
from django.db import models
from django.db.models import Q

from core.models import Classifier, Organization
from django.utils.translation import gettext_lazy as _

from users.signals import ConstantGroups


class User(AbstractUser):
    classifier = models.ForeignKey(
        Classifier,
        verbose_name=_("classifier"),
        null=True,
        blank=True,
        on_delete=models.CASCADE,
        related_name="workers",
    )
    organization = models.ForeignKey(
        Organization,
        verbose_name=_("organization"),
        null=True,
        blank=True,
        on_delete=models.CASCADE,
        related_name="workers",
    )

    enable_file_upload_only_from_camera = models.BooleanField(
        default=False, verbose_name=_("enable file upload only from camera")
    )

    class Meta:
        constraints = [
            models.CheckConstraint(
                check=(Q(classifier__isnull=True) & Q(organization__isnull=True))
                | (Q(classifier__isnull=False) & Q(organization__isnull=False)),
                name="classifier_and_organization_use_together",
                violation_error_message=_("Classifier and Organization must be used | not used together"),
            ),
        ]

        verbose_name = _("User")
        verbose_name_plural = _("Users")

    def __str__(self):
        return self.username

    @property
    def is_worker(self) -> bool:
        return self.groups.filter(name=ConstantGroups.WORKER).exists()

    @property
    def is_supervisor(self) -> bool:
        return self.groups.filter(name=ConstantGroups.SUPERVISOR).exists()

    @property
    def is_admin(self) -> bool:
        return self.groups.filter(name=ConstantGroups.ADMIN).exists() or self.is_staff or self.is_superuser
