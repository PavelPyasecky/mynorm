from django.db import models
from django.utils import timezone


class CreatedUpdatedMixin(models.Model):
    created_by = models.ForeignKey('users.User', on_delete=models.SET_NULL, related_name="%(class)s_created", null=True, blank=True)
    updated_by = models.ForeignKey('users.User', on_delete=models.SET_NULL, related_name="%(class)s_updated", null=True, blank=True)
    created_date = models.DateTimeField(default=timezone.now)
    updated_date = models.DateTimeField(default=timezone.now)

    class Meta:
        abstract = True


class StartEndDateMixin(models.Model):
    start_date = models.DateTimeField(default=timezone.now)
    end_date = models.DateTimeField(null=True, blank=True)

    class Meta:
        abstract = True
