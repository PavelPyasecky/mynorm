import pandas as pd
from io import BytesIO

import pytz
from django.db.models import Value, ExpressionWrapper, F, fields, Prefetch, Sum, DurationField, CharField, Case, When, \
    Func, Count, OuterRef, Subquery, IntegerField
from django.db.models.functions import Concat, Coalesce, Extract
from django.utils import timezone
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import status, filters
from rest_framework.decorators import action
from rest_framework.generics import get_object_or_404
from rest_framework.mixins import (
    ListModelMixin,
    CreateModelMixin,
    RetrieveModelMixin, UpdateModelMixin, DestroyModelMixin,
)
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet
from drf_spectacular.utils import extend_schema, extend_schema_view, OpenApiParameter, OpenApiExample
from drf_spectacular.types import OpenApiTypes

from analytics import serializers, exceptions
from analytics.exceptions import AnalyticsDoesNotExistException
from analytics.filters import SupervisionDateFilter
from analytics.models import (
    ActivityStatistics,
    Supervision,
    Comment,
    CommentFiles,
    CommentImage,
)
from analytics.services import (
    SupervisionService,
    FailureService,
    ActivityStatisticsService,
)
from core import paginators
from core.permissions import CustomDjangoModelPermissions
from core.utils import localize_datetime, timedelta_to_str, success_response
from users.signals import ConstantGroups
from django.utils.translation import gettext_lazy as _


class AnalyticsListView(ListModelMixin, GenericViewSet):
    permission_classes = (CustomDjangoModelPermissions,)
    serializer_class = serializers.AnalyticsDetailsSerializer
    queryset = ActivityStatistics.objects.all()
    ordering = ["start_date"]

    def get_queryset(self):
        supervision_id = self.kwargs.get("pk")
        get_object_or_404(Supervision, id=supervision_id)
        return self.queryset.filter(supervision_id=supervision_id)


class AnalyticsCreateViewSet(CreateModelMixin, GenericViewSet):
    permission_classes = (CustomDjangoModelPermissions,)
    serializer_class = serializers.AnalyticsCreateSerializer
    queryset = ActivityStatistics.objects.all()

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        supervision_id = self.kwargs.get("pk")
        get_object_or_404(Supervision, id=supervision_id)
        serializer.validated_data["supervision_id"] = supervision_id

        previous_activity_statistic = ActivityStatistics.objects.filter(
            supervision_id=supervision_id, end_date__isnull=True
        ).last()
        new_activity = serializer.validated_data["activity"]
        activity_statistic = ActivityStatisticsService().start_activity(
            serializer.validated_data,
            previous_activity_statistic,
            new_activity,
        )
        serializer = self.get_serializer(activity_statistic)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


@extend_schema_view(
    list=extend_schema(
        summary="List supervisions",
        description="Retrieve a paginated list of supervisions with filtering, searching, and ordering options.",
        tags=["Analytics"],
        parameters=[
            OpenApiParameter(
                name="search",
                type=OpenApiTypes.STR,
                location=OpenApiParameter.QUERY,
                description="Search supervisions by ID, organization name, worker name, or user name"
            ),
            OpenApiParameter(
                name="organization",
                type=OpenApiTypes.INT,
                location=OpenApiParameter.QUERY,
                description="Filter by organization ID"
            ),
            OpenApiParameter(
                name="worker",
                type=OpenApiTypes.INT,
                location=OpenApiParameter.QUERY,
                description="Filter by worker ID"
            ),
            OpenApiParameter(
                name="user",
                type=OpenApiTypes.INT,
                location=OpenApiParameter.QUERY,
                description="Filter by user ID"
            ),
            OpenApiParameter(
                name="verified",
                type=OpenApiTypes.BOOL,
                location=OpenApiParameter.QUERY,
                description="Filter by verification status"
            ),
            OpenApiParameter(
                name="ordering",
                type=OpenApiTypes.STR,
                location=OpenApiParameter.QUERY,
                description="Order results by field (prefix with - for descending)"
            ),
            OpenApiParameter(
                name="start_date",
                type=OpenApiTypes.DATE,
                location=OpenApiParameter.QUERY,
                description="Filter by start date (YYYY-MM-DD). When both start_date and end_date are provided and different, filters supervisions where both their start_date and end_date fall within the range. When both dates are the same, shows supervisions active on that date."
            ),
            OpenApiParameter(
                name="end_date",
                type=OpenApiTypes.DATE,
                location=OpenApiParameter.QUERY,
                description="Filter by end date (YYYY-MM-DD). When both start_date and end_date are provided and different, filters supervisions where both their start_date and end_date fall within the range. When both dates are the same, shows supervisions active on that date."
            )
        ],
        responses={
            200: serializers.SupervisionListSerializer(many=True),
            403: {"description": "Permission denied"}
        }
    ),
    retrieve=extend_schema(
        summary="Get supervision",
        description="Retrieve a specific supervision by ID with detailed information.",
        tags=["Analytics"],
        responses={
            200: serializers.SupervisionSerializer,
            404: {"description": "Supervision not found"},
            403: {"description": "Permission denied"}
        }
    ),
    create=extend_schema(
        summary="Create supervision",
        description="Create a new supervision session.",
        tags=["Analytics"],
        request=serializers.SupervisionCreateSerializer,
        responses={
            201: serializers.SupervisionSerializer,
            400: {"description": "Bad request - validation errors"},
            403: {"description": "Permission denied"}
        }
    ),
    update=extend_schema(
        summary="Update supervision",
        description="Update a supervision session.",
        tags=["Analytics"],
        request=serializers.SupervisionUpdateSerializer,
        responses={
            200: serializers.SupervisionSerializer,
            400: {"description": "Bad request - validation errors"},
            404: {"description": "Supervision not found"},
            403: {"description": "Permission denied"}
        }
    ),
    partial_update=extend_schema(
        summary="Partially update supervision",
        description="Partially update a supervision session.",
        tags=["Analytics"],
        request=serializers.SupervisionUpdateSerializer,
        responses={
            200: serializers.SupervisionSerializer,
            400: {"description": "Bad request - validation errors"},
            404: {"description": "Supervision not found"},
            403: {"description": "Permission denied"}
        }
    ),
    destroy=extend_schema(
        summary="Delete supervision",
        description="Delete a supervision session by ID.",
        tags=["Analytics"],
        responses={
            204: {"description": "Supervision deleted successfully"},
            404: {"description": "Supervision not found"},
            403: {"description": "Permission denied"}
        }
    )
)
class SupervisionViewSet(
    RetrieveModelMixin, CreateModelMixin, ListModelMixin, UpdateModelMixin, DestroyModelMixin, GenericViewSet
):
    """
    ViewSet for managing supervision sessions.
    Provides CRUD operations for Supervision model with advanced filtering and export capabilities.
    """
    permission_classes = (CustomDjangoModelPermissions,)
    serializer_class = serializers.SupervisionSerializer
    queryset = Supervision.objects.all()
    pagination_class = paginators.CustomPagination
    filter_backends = (filters.SearchFilter, DjangoFilterBackend, SupervisionDateFilter, filters.OrderingFilter)
    filterset_fields = ('id', 'organization', 'worker', 'user', 'verified')
    search_fields = (
        'id',
        'organization__name',
        'worker__first_name',
        'worker__last_name',
        'user__first_name',
        'user__last_name',
    )
    ordering_fields = ('id', 'organization_id', 'worker_id', 'user_id', 'start_date', 'end_date', 'delta', 'verified')
    ordering = ('-id',)

    EXPORT_FILE_NAME = 'Mera_Export_Supervision'

    def get_serializer_class(self):
        if self.action in ("list", "export", "last_active_supervision"):
            return serializers.SupervisionListSerializer
        elif self.action == "retrieve":
            return serializers.SupervisionSerializer
        elif self.action in ("create",):
            return serializers.SupervisionCreateSerializer
        elif self.action in ("partial_update", "update"):
            return serializers.SupervisionUpdateSerializer

    def get_queryset(self):
        qs = self.queryset

        if self.action in ("list", "export", "last_active_supervision"):
            activity_count_subquery = ActivityStatistics.objects.filter(
                supervision=OuterRef('pk')
            ).annotate(
                actual_duration=Extract(F('end_date') - F('start_date'), 'epoch'),
                planned_duration=Extract(
                    F('activity__planned_end_time') - F('activity__planned_start_time'),
                    'epoch'
                )
            ).filter(
                actual_duration__gt=F('planned_duration'),
                end_date__isnull=False,
                start_date__isnull=False,
                activity__planned_end_time__isnull=False,
                activity__planned_start_time__isnull=False
            ).values('supervision').annotate(
                count=Count('id')
            ).values('count')

            qs = (self.queryset.select_related("organization", "worker", "user").prefetch_related(
                Prefetch(
                    "statistics",
                    queryset=ActivityStatistics.objects.select_related("failure", "activity").prefetch_related(
                        Prefetch(
                            "comments",
                            queryset=Comment.objects.select_related("created_by").prefetch_related("created_by__groups").filter(
                                created_by__groups__name=ConstantGroups.SUPERVISOR
                            )
                        ),
                    )
                ),
            ).annotate(
                total_failure_delta=Sum(
                    F('statistics__failure__end_date') - F('statistics__failure__start_date'),
                    output_field=DurationField()
                )
            ).annotate(
                display_total_failure_delta=Case(
                    When(total_failure_delta__isnull=True, then=Value('--:--:--')),
                    default=Func(
                        F('total_failure_delta'),
                        function='TO_CHAR',
                        template="%(function)s(%(expressions)s, 'HH24:MI:SS')"
                    ),
                    output_field=CharField()
                ),
                overtime_activities_count=Coalesce(
                    Subquery(activity_count_subquery),
                    0,
                    output_field=IntegerField()
                )
            ))

        return qs

    def create(self, request, *args, **kwargs):
        last_supervision = Supervision.objects.filter(user=request.user).order_by("-id").first()
        if last_supervision and last_supervision.end_date is None:
            raise exceptions.SupervisionIsNotFinishedException()

        return super().create(request, *args, **kwargs)

    @extend_schema(
        summary="Finish supervision",
        description="Mark a supervision session as finished.",
        tags=["Analytics"],
        responses={
            200: {
                "type": "object",
                "properties": {
                    "details": {"type": "string", "example": "Success."}
                }
            },
            404: {"description": "Supervision not found"},
            403: {"description": "Permission denied"}
        }
    )
    def finish(self, request: Request, pk: int):
        supervision = get_object_or_404(Supervision.objects, pk=pk)
        SupervisionService().finish_supervision(supervision)

        return success_response()

    @extend_schema(
        summary="Verify supervision",
        description="Mark a supervision session as verified.",
        tags=["Analytics"],
        responses={
            200: {
                "type": "object",
                "properties": {
                    "details": {"type": "string", "example": "Success."}
                }
            },
            404: {"description": "Supervision not found"},
            403: {"description": "Permission denied"}
        }
    )
    def verify(self, request: Request, pk: int):
        supervision = get_object_or_404(Supervision.objects, pk=pk)
        SupervisionService().verify(supervision)

        return success_response()

    @extend_schema(
        summary="Clear supervision verification",
        description="Clear the verification status of a supervision session.",
        tags=["Analytics"],
        responses={
            200: {
                "type": "object",
                "properties": {
                    "details": {"type": "string", "example": "Success."}
                }
            },
            404: {"description": "Supervision not found"},
            403: {"description": "Permission denied"}
        }
    )
    def clear_verification(self, request: Request, pk: int):
        supervision = get_object_or_404(Supervision.objects, pk=pk)
        SupervisionService().clear_verification(supervision)

        return success_response()

    @extend_schema(
        summary="Delete not verified supervisions",
        description="Delete supervisions that are not verified. Supports filtering, searching, and ordering via query parameters.",
        tags=["Analytics"],
        parameters=[
            OpenApiParameter(
                name="search",
                type=OpenApiTypes.STR,
                location=OpenApiParameter.QUERY,
                description="Search supervisions by ID, organization name, worker name, or user name"
            ),
            OpenApiParameter(
                name="organization",
                type=OpenApiTypes.INT,
                location=OpenApiParameter.QUERY,
                description="Filter by organization ID"
            ),
            OpenApiParameter(
                name="worker",
                type=OpenApiTypes.INT,
                location=OpenApiParameter.QUERY,
                description="Filter by worker ID"
            ),
            OpenApiParameter(
                name="user",
                type=OpenApiTypes.INT,
                location=OpenApiParameter.QUERY,
                description="Filter by user ID"
            ),
            OpenApiParameter(
                name="verified",
                type=OpenApiTypes.BOOL,
                location=OpenApiParameter.QUERY,
                description="Filter by verification status"
            ),
            OpenApiParameter(
                name="ordering",
                type=OpenApiTypes.STR,
                location=OpenApiParameter.QUERY,
                description="Order results by field (prefix with - for descending)"
            )
        ],
        responses={
            200: {
                "type": "object",
                "properties": {
                    "deleted_entities_count": {"type": "integer", "example": 5},
                    "deleted_entities": {
                        "type": "object",
                        "example": {"analytics.Supervision": 5}
                    }
                }
            },
            403: {"description": "Permission denied"}
        }
    )
    def delete_not_verified(self, request):
        # Apply the same filtering, searching, and ordering as list method
        queryset = self.filter_queryset(self.get_queryset())
        # Filter only not verified supervisions
        queryset = queryset.filter(verified=False)
        
        deleted_entities_count, deleted_entities_dict = queryset.delete()
        data = {
            "deleted_entities_count": deleted_entities_count,
            "deleted_entities": deleted_entities_dict,
        }
        return Response(data=data, status=status.HTTP_200_OK)

    def last_active_supervision(self, request):
        supervision = SupervisionService().get_user_last_active_supervision(request.user)
        if supervision:
            serializer = self.get_serializer(supervision)
            return Response(data=serializer.data, status=status.HTTP_200_OK)
        return Response({"details": _("No active supervision.")}, status=status.HTTP_200_OK)

    @extend_schema(
        summary="Export supervisions",
        description="Export verified supervisions to Excel format with detailed analytics data.",
        tags=["Analytics"],
        parameters=[
            OpenApiParameter(
                name="timezone",
                type=OpenApiTypes.STR,
                location=OpenApiParameter.QUERY,
                description="Timezone for date formatting (default: Europe/Moscow)",
                default="Europe/Moscow"
            )
        ],
        responses={
            200: {
                "description": "Excel file with supervision data",
                "content": {
                    "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet": {
                        "schema": {"type": "string", "format": "binary"}
                    }
                }
            },
            403: {"description": "Permission denied"}
        }
    )
    @action(detail=False, methods=['get'])
    def export(self, request):
        tz_param = request.query_params.get('timezone', 'Europe/Moscow')
        target_tz = pytz.timezone(tz_param)

        queryset = self.filter_queryset(self.get_queryset())

        data = queryset.filter(
            verified=True
        ).annotate(
            worker_full_name=Concat('worker__first_name', Value(' '), 'worker__last_name'),
            viewer_full_name=Concat('user__first_name', Value(' '), 'user__last_name'),
            duration=ExpressionWrapper(
                F('end_date') - F('start_date'),
                output_field=fields.DurationField()
            ),
            analytics_duration=ExpressionWrapper(
                F('statistics__end_date') - F('statistics__start_date'),
                output_field=fields.DurationField()
            ),
            analytics_failure_duration=ExpressionWrapper(
                F('statistics__failure__end_date') - F('statistics__failure__start_date'),
                output_field=fields.DurationField()
            ),
        ).values(
            'id',
            'organization__name',
            'worker__classifier__name',
            'worker__classifier__code',
            'worker_full_name',
            'viewer_full_name',
            'validity',
            'verified',
            'start_date',
            'end_date',
            'duration',
            'statistics__id',
            'statistics__activity__name',
            'statistics__failure__start_date',
            'statistics__failure__end_date',
            'analytics_failure_duration',
            'statistics__start_date',
            'statistics__end_date',
            'analytics_duration',
        ).order_by(
            '-id',
            '-statistics__id',
        )

        df = pd.DataFrame(data)

        for field_name in df.columns:
            if 'date' in field_name.split('_'):
                df[field_name] = pd.to_datetime(df[field_name], errors='coerce')

                df[field_name] = df[field_name].apply(
                    lambda x: x.astimezone(target_tz).replace(tzinfo=None)
                    if pd.notna(x) else None
                )

            if 'duration' in field_name.split('_'):
                df[field_name] = [
                    timedelta_to_str(td) if pd.notna(td) else '--:--:--'
                    for td in df[field_name]
                ]

        df.rename(columns={
            'id': 'ID Наблюдения',
            'organization__name': 'Название организации',
            'worker__classifier__name': "Название классификатора",
            'worker__classifier__code': "Код классификатора",
            'worker_full_name': "ФИО Работника",
            'viewer_full_name': "ФИО Наблюдателя",
            'validity': "Наличие сбоев",
            'verified': "Проверенно",
            'start_date': "Начало наблюдения",
            'end_date': "Конец наблюдения",
            'duration': "Длительность наблюдения",
            'statistics__id': "ID аналитики",
            'statistics__activity__name': "Название операции",
            'statistics__start_date': "Начало операции",
            'statistics__end_date': "Конец операции",
            'analytics_duration': "Длительность операции",
            'statistics__failure__start_date': "Начало сбоя операции",
            'statistics__failure__end_date': "Конец сбоя операции",
            'analytics_failure_duration': "Длительность сбоя суммарная",
        }, inplace=True)

        output = BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            df.to_excel(writer, sheet_name='Supervisions', index=False)

        converted_datetime = localize_datetime(timezone.now(), target_tz)
        str_datetime = converted_datetime.strftime("%d_%m_%y__%H_%M_%S")
        file_name = f'{self.EXPORT_FILE_NAME}__{str_datetime}'

        response = Response(
            content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )
        response['Content-Disposition'] = f'attachment; filename={file_name}.xlsx'
        response.content = output.getvalue()

        return response


class AnalyticsCommentView(CreateModelMixin, UpdateModelMixin, GenericViewSet):
    permission_classes = (CustomDjangoModelPermissions,)
    serializer_class = serializers.CommentCreateSerializer
    queryset = Comment.objects.all()

    def perform_create(self, serializer):
        activity_statistics_id = self.kwargs.get("analytics_id")

        activity_statistics = ActivityStatistics.objects.filter(id=activity_statistics_id).first()

        if not activity_statistics:
            raise AnalyticsDoesNotExistException()

        text = serializer.validated_data.get("text")
        images = serializer.validated_data.get("images")
        files = serializer.validated_data.get("files")
        coordinates = serializer.validated_data.get("coordinates")

        if text or images or files:
            comment = Comment.objects.create(
                activity_statistics_id=activity_statistics_id,
                text=text,
                coordinates=coordinates,
                created_by=self.request.user,
                updated_by=self.request.user,
            )

            if images:
                image_objects = []
                for image in images:
                    comment_image = CommentImage(comment=comment, image=image)
                    image_objects.append(comment_image)

                CommentImage.objects.bulk_create(image_objects)

            if files:
                file_objects = []
                for file in files:
                    comment_file = CommentFiles(comment=comment, file=file)
                    file_objects.append(comment_file)

                CommentFiles.objects.bulk_create(file_objects)

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        instance = self.perform_update(serializer)

        return Response(serializers.CommentSerializer(instance).data)

    def perform_update(self, serializer):
        return serializer.save()


class AnalyticsFailureView(GenericViewSet):
    permission_classes = (CustomDjangoModelPermissions,)
    serializer_class = serializers.FailureSerializer
    queryset = Comment.objects.all()

    def _get_activity_statistics(self) -> ActivityStatistics:
        supervision_id = self.kwargs.get("supervision_id")
        activity_id = self.kwargs.get("activity_id")
        activity_statistics = ActivityStatistics.objects.filter(
            supervision_id=supervision_id, activity_id=activity_id, end_date__isnull=True).order_by("-id").first()

        if not activity_statistics:
            raise exceptions.ActivityFailureException()

        return activity_statistics

    def start_failure(self, request, *args, **kwargs):
        activity_statistics = self._get_activity_statistics()
        failure = FailureService().create_failure(activity_statistics)

        serializer = self.get_serializer(failure)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def finish_failure(self, request, *args, **kwargs):
        activity_statistics = self._get_activity_statistics()

        failure = FailureService().finish_failure(activity_statistics)

        serializer = self.get_serializer(failure)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class AnalyticsDetailsView(RetrieveModelMixin, UpdateModelMixin, GenericViewSet):
    permission_classes = (CustomDjangoModelPermissions,)
    serializer_class = serializers.AnalyticsDetailsSerializer
    queryset = ActivityStatistics.objects.prefetch_related("comments")
    lookup_field = "pk"

    def get_serializer_class(self):
        if self.action == "retrieve":
            return serializers.AnalyticsDetailsSerializer

        elif self.action in ("partial_update", "update"):
            return serializers.AnalyticsUpdateSerializer

    @extend_schema(
        summary="Verify activity statistics",
        description="Mark activity statistics as verified.",
        tags=["Analytics"],
        responses={
            200: {
                "type": "object",
                "properties": {
                    "details": {"type": "string", "example": "Success."}
                }
            },
            404: {"description": "Activity statistics not found"},
            403: {"description": "Permission denied"}
        }
    )
    def verify(self, request: Request, pk: int):
        activity_statistics = get_object_or_404(ActivityStatistics.objects, pk=pk)
        ActivityStatisticsService().verify(activity_statistics)

        return success_response()

    @extend_schema(
        summary="Clear activity statistics verification",
        description="Clear the verification status of activity statistics.",
        tags=["Analytics"],
        responses={
            200: {
                "type": "object",
                "properties": {
                    "details": {"type": "string", "example": "Success."}
                }
            },
            404: {"description": "Activity statistics not found"},
            403: {"description": "Permission denied"}
        }
    )
    def clear_verification(self, request: Request, pk: int):
        activity_statistics = get_object_or_404(ActivityStatistics.objects, pk=pk)
        ActivityStatisticsService().clear_verification(activity_statistics)

        return success_response()
