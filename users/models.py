from django.contrib.auth.models import AbstractUser
from django.db import models
from django.db.models import Q

from core.models import Classifier, Organization
from django.utils.translation import gettext_lazy as _


class User(AbstractUser):
    classifier = models.ForeignKey(Classifier, null=True, blank=True, on_delete=models.CASCADE, related_name='workers')
    organization = models.ForeignKey(Organization, null=True, blank=True, on_delete=models.CASCADE, related_name='workers')

    class Meta:
        constraints = [
            models.CheckConstraint(
                check=(Q(is_staff=True) & Q(organization__isnull=True)) |
                      (Q(is_staff=False) & Q(organization__isnull=False)),
                name='organization_required_only_for_workers'
            ),
            models.CheckConstraint(
                check=(Q(is_staff=True) & Q(classifier__isnull=True)) |
                      (Q(is_staff=False) & Q(classifier__isnull=False)),
                name='classifier_required_only_for_workers'
            ),
            models.UniqueConstraint(
                fields=['classifier', 'organization'],
                name='unique_classifier_organization_of_user_if_set',
                condition=Q(classifier__isnull=False, organization__isnull=False)
            )
        ]

    def __str__(self):
        return self.username

    @property
    def is_worker(self) -> bool:
        return bool(self.classifier)

    @property
    def is_supervisor(self) -> bool:
        return not bool(self.classifier)
