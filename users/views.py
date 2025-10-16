from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters
from rest_framework.mixins import ListModelMixin, RetrieveModelMixin
from rest_framework.viewsets import GenericViewSet
from drf_spectacular.utils import extend_schema, extend_schema_view, OpenApiParameter
from drf_spectacular.types import OpenApiTypes

from core.permissions import CustomDjangoModelPermissions
from users import serializers
from users.filters import UserFilter
from users.models import User


@extend_schema_view(
    list=extend_schema(
        summary="List users",
        description="Retrieve a list of users with optional filtering and searching.",
        tags=["Users"],
        parameters=[
            OpenApiParameter(
                name="search",
                type=OpenApiTypes.STR,
                location=OpenApiParameter.QUERY,
                description="Search users by username, first name, or last name"
            ),
            OpenApiParameter(
                name="organization",
                type=OpenApiTypes.INT,
                location=OpenApiParameter.QUERY,
                description="Filter by organization ID"
            ),
            OpenApiParameter(
                name="classifier",
                type=OpenApiTypes.INT,
                location=OpenApiParameter.QUERY,
                description="Filter by classifier ID"
            )
        ],
        responses={
            200: serializers.UserSerializer(many=True),
            403: {"description": "Permission denied"}
        }
    ),
    retrieve=extend_schema(
        summary="Get user",
        description="Retrieve a specific user by ID with detailed information.",
        tags=["Users"],
        responses={
            200: serializers.UserDetailsSerializer,
            404: {"description": "User not found"},
            403: {"description": "Permission denied"}
        }
    )
)
class UserListView(ListModelMixin, RetrieveModelMixin, GenericViewSet):
    """
    ViewSet for managing users.
    Provides list and retrieve operations for User model with filtering and search capabilities.
    """
    permission_classes = (CustomDjangoModelPermissions,)
    serializer_class = serializers.UserSerializer
    queryset = User.objects.all()

    filter_backends = [filters.SearchFilter, UserFilter, DjangoFilterBackend]
    filterset_fields = ("organization", "classifier")
    search_fields = ["username", "first_name", "last_name"]

    def get_serializer_class(self):
        if self.action == "retrieve":
            return serializers.UserDetailsSerializer

        return serializers.UserSerializer
