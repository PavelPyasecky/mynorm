from django.shortcuts import get_object_or_404
from rest_framework.exceptions import ValidationError
from rest_framework.mixins import ListModelMixin
from rest_framework.viewsets import GenericViewSet

from analytics.models import Supervision
from core.permissions import CustomDjangoModelPermissions
from layouts import serializers
from layouts.models import Layout


class LayoutViewSet(ListModelMixin, GenericViewSet):
    permission_classes = (CustomDjangoModelPermissions,)
    serializer_class = serializers.LayoutSerializer
    queryset = Layout.objects.all().prefetch_related(
        "activity_groups", "activity_groups__activities"
    )

    def get_queryset(self):
        qs = super().get_queryset()

        supervision_id = self.request.query_params.get("supervision_id", None)

        if not supervision_id:
            raise ValidationError(
                "The required query parameter `supervision_id` is missing"
            )
        supervision = get_object_or_404(Supervision.objects, id=supervision_id)
        qs = qs.filter(classifier_id=supervision.worker.classifier_id)

        return qs
