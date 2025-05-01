from django.db import models
from ordered_model.models import OrderedModel

from core.model_mixins import CreatedUpdatedMixin
from core.models import Organization, Classifier


class Layout(OrderedModel, CreatedUpdatedMixin):
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE, related_name='layouts')
    classifier = models.OneToOneField(Classifier, on_delete=models.CASCADE, related_name='layout')

    def __str__(self):
        return f"Layout {self.id}"


class ActivityGroup(OrderedModel, CreatedUpdatedMixin):
    name = models.CharField(max_length=255)
    layout = models.ForeignKey(Layout, on_delete=models.CASCADE, related_name='activity_groups')

    order_with_respect_to = 'layout'

    def __str__(self):
        return self.name


class Activity(OrderedModel, CreatedUpdatedMixin):
    name = models.CharField(max_length=255)
    activity_group = models.ForeignKey(ActivityGroup, on_delete=models.CASCADE, related_name='activities')

    order_with_respect_to = 'activity_group'

    def __str__(self):
        return self.name
