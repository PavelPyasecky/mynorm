from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters
from rest_framework.mixins import ListModelMixin, RetrieveModelMixin
from rest_framework.viewsets import GenericViewSet
from drf_spectacular.utils import extend_schema, extend_schema_view, OpenApiParameter, OpenApiExample
from drf_spectacular.types import OpenApiTypes

from core import serializers
from core.models import Organization, Classifier
from core.permissions import IsSupervisor, IsSupervisorGroup, CustomDjangoModelPermissions


@extend_schema_view(
    list=extend_schema(
        summary="List organizations",
        description="Retrieve a list of organizations with optional search and filtering.",
        tags=["Core"],
        parameters=[
            OpenApiParameter(
                name="search",
                type=OpenApiTypes.STR,
                location=OpenApiParameter.QUERY,
                description="Search organizations by name"
            )
        ],
        responses={
            200: serializers.OrganizationSerializer(many=True),
            403: {"description": "Permission denied"}
        }
    ),
    retrieve=extend_schema(
        summary="Get organization",
        description="Retrieve a specific organization by ID.",
        tags=["Core"],
        responses={
            200: serializers.OrganizationSerializer,
            404: {"description": "Organization not found"},
            403: {"description": "Permission denied"}
        }
    )
)
class OrganizationListView(ListModelMixin, RetrieveModelMixin, GenericViewSet):
    """
    ViewSet for managing organizations.
    Provides list and retrieve operations for Organization model.
    """
    permission_classes = (CustomDjangoModelPermissions,)
    serializer_class = serializers.OrganizationSerializer
    queryset = Organization.objects.all()

    filter_backends = [filters.SearchFilter, DjangoFilterBackend]
    search_fields = ("name",)


@extend_schema_view(
    list=extend_schema(
        summary="List classifiers",
        description="Retrieve a list of classifiers with optional search and filtering.",
        tags=["Core"],
        parameters=[
            OpenApiParameter(
                name="search",
                type=OpenApiTypes.STR,
                location=OpenApiParameter.QUERY,
                description="Search classifiers by code or name"
            )
        ],
        responses={
            200: serializers.ClassifierSerializer(many=True),
            403: {"description": "Permission denied"}
        }
    ),
    retrieve=extend_schema(
        summary="Get classifier",
        description="Retrieve a specific classifier by ID.",
        tags=["Core"],
        responses={
            200: serializers.ClassifierSerializer,
            404: {"description": "Classifier not found"},
            403: {"description": "Permission denied"}
        }
    )
)
class ClassifierListView(ListModelMixin, RetrieveModelMixin, GenericViewSet):
    """
    ViewSet for managing classifiers.
    Provides list and retrieve operations for Classifier model.
    """
    permission_classes = (CustomDjangoModelPermissions,)
    serializer_class = serializers.ClassifierSerializer
    queryset = Classifier.objects.all()

    filter_backends = [filters.SearchFilter, DjangoFilterBackend]
    search_fields = (
        "code",
        "name",
    )
