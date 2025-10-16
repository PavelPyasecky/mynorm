from rest_framework import status
from rest_framework.decorators import action
from rest_framework.mixins import RetrieveModelMixin, UpdateModelMixin
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet
from drf_spectacular.utils import extend_schema, extend_schema_view, OpenApiParameter, OpenApiExample
from drf_spectacular.types import OpenApiTypes

from app_settings import serializers
from app_settings.models import AppSetting
from core.permissions import CustomDjangoModelPermissions


@extend_schema_view(
    retrieve=extend_schema(
        summary="Get application settings",
        description="Retrieve the current application settings singleton.",
        tags=["App Settings"],
        responses={
            200: serializers.AppSettingSerializer,
            500: {"description": "Internal server error"}
        }
    ),
    update=extend_schema(
        summary="Update application settings",
        description="Update the application settings singleton.",
        tags=["App Settings"],
        request=serializers.AppSettingSerializer,
        responses={
            200: serializers.AppSettingSerializer,
            400: {"description": "Bad request - validation errors"},
            500: {"description": "Internal server error"}
        }
    ),
    partial_update=extend_schema(
        summary="Partially update application settings",
        description="Partially update the application settings singleton.",
        tags=["App Settings"],
        request=serializers.AppSettingSerializer,
        responses={
            200: serializers.AppSettingSerializer,
            400: {"description": "Bad request - validation errors"},
            500: {"description": "Internal server error"}
        }
    )
)
class AppSettingViewSet(RetrieveModelMixin, UpdateModelMixin, GenericViewSet):
    """
    ViewSet for managing application settings singleton.
    Provides retrieve and update operations for the single AppSetting instance.
    """
    permission_classes = (CustomDjangoModelPermissions,)
    serializer_class = serializers.AppSettingSerializer
    
    def get_object(self):
        """
        Always return the singleton instance.
        """
        return AppSetting.load()

    @extend_schema(
        summary="Get current application settings",
        description="Get the current application settings. This endpoint always returns the singleton instance.",
        tags=["App Settings"],
        responses={
            200: serializers.AppSettingSerializer,
            500: {"description": "Internal server error"}
        }
    )
    @action(detail=False, methods=['get'])
    def current(self, request):
        """
        Get the current application settings.
        Always returns the singleton instance.
        """
        try:
            app_setting = AppSetting.load()
            serializer = self.get_serializer(app_setting)
            return Response(serializer.data)
        except Exception as e:
            return Response(
                {"error": "Failed to retrieve application settings"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @extend_schema(
        summary="Update current application settings",
        description="Update the current application settings. Updates the singleton instance.",
        tags=["App Settings"],
        request=serializers.AppSettingSerializer,
        responses={
            200: serializers.AppSettingSerializer,
            400: {"description": "Bad request - validation errors"},
            500: {"description": "Internal server error"}
        },
        examples=[
            OpenApiExample(
                "Update settings example",
                summary="Example request body",
                description="Example of updating application settings",
                value={
                    "hide_failure_btn": True,
                    "hide_info_btn": False
                }
            )
        ]
    )
    @action(detail=False, methods=['post', 'put', 'patch'])
    def update_current(self, request):
        """
        Update the current application settings.
        Updates the singleton instance.
        """
        try:
            app_setting = AppSetting.load()
            serializer = self.get_serializer(app_setting, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response(
                {"error": "Failed to update application settings"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
