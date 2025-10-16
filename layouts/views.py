from django.shortcuts import get_object_or_404
from rest_framework.exceptions import ValidationError
from rest_framework.mixins import ListModelMixin
from rest_framework.viewsets import GenericViewSet
from drf_spectacular.utils import extend_schema, extend_schema_view, OpenApiParameter
from drf_spectacular.types import OpenApiTypes

from analytics.models import Supervision
from core.permissions import CustomDjangoModelPermissions
from layouts import serializers
from layouts.models import Layout


@extend_schema_view(
    list=extend_schema(
        summary="List layouts",
        description="Retrieve layouts filtered by supervision's worker classifier.",
        tags=["Layouts"],
        parameters=[
            OpenApiParameter(
                name="supervision_id",
                type=OpenApiTypes.INT,
                location=OpenApiParameter.QUERY,
                description="ID of the supervision to get layouts for",
                required=True
            )
        ],
        responses={
            200: serializers.LayoutSerializer(many=True),
            400: {"description": "Bad request - supervision_id parameter missing"},
            404: {"description": "Supervision not found"},
            403: {"description": "Permission denied"}
        }
    )
)
class LayoutViewSet(ListModelMixin, GenericViewSet):
    """
    ViewSet for managing layouts.
    Provides list operation for Layout model filtered by supervision's worker classifier.
    """
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
