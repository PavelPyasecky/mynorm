import pandas as pd
from io import BytesIO

import pytz
from django.db.models import Value, ExpressionWrapper, F, fields, Prefetch, Sum, DurationField, CharField, Case, When, \
    Func, Count, Q, OuterRef, Subquery, IntegerField
from django.db.models.functions import Concat, Coalesce, Extract
from django.utils import timezone
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import status, filters
from rest_framework.decorators import action
from rest_framework.generics import get_object_or_404
from rest_framework.mixins import (
    ListModelMixin,
    CreateModelMixin,
    RetrieveModelMixin, UpdateModelMixin,
)
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet

from analytics import serializers, exceptions
from analytics.exceptions import AnalyticsDoesNotExistException
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
from core.permissions import IsSupervisor
from core.utils import localize_datetime, timedelta_to_str


class AnalyticsListView(ListModelMixin, GenericViewSet):
    permission_classes = (IsSupervisor,)
    serializer_class = serializers.AnalyticsDetailsSerializer
    queryset = ActivityStatistics.objects.all()
    ordering = ["start_date"]

    def get_queryset(self):
        supervision_id = self.kwargs.get("pk")
        get_object_or_404(Supervision, id=supervision_id)
        return self.queryset.filter(supervision_id=supervision_id)


class AnalyticsCreateViewSet(CreateModelMixin, GenericViewSet):
    permission_classes = (IsSupervisor,)
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


class SupervisionViewSet(
    RetrieveModelMixin, CreateModelMixin, ListModelMixin, UpdateModelMixin, GenericViewSet
):
    permission_classes = (IsSupervisor,)
    serializer_class = serializers.SupervisionSerializer
    queryset = Supervision.objects.all()
    pagination_class = paginators.CustomPagination
    filter_backends = (filters.SearchFilter, DjangoFilterBackend, filters.OrderingFilter)
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
        if self.action in ("list", "export"):
            return serializers.SupervisionListSerializer
        elif self.action == "retrieve":
            return serializers.SupervisionSerializer
        elif self.action in ("create",):
            return serializers.SupervisionCreateSerializer
        elif self.action in ("partial_update", "update"):
            return serializers.SupervisionUpdateSerializer

    def get_queryset(self):
        qs = self.queryset

        if self.action == "list":
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

            qs = self.queryset.select_related("organization", "worker", "user").prefetch_related(
                Prefetch("statistics", queryset=ActivityStatistics.objects.select_related("failure", "activity")),
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
            )

        return qs

    def create(self, request, *args, **kwargs):
        last_supervision = Supervision.objects.filter(user=request.user).order_by("-id").first()
        if last_supervision.end_date is None:
            raise exceptions.SupervisionIsNotFinishedException()

        return super().create(request, *args, **kwargs)

    def finish(self, request: Request, pk: int):
        supervision = get_object_or_404(Supervision.objects, pk=pk)
        SupervisionService().finish_supervision(supervision)

        return Response(status=status.HTTP_200_OK)

    def verify(self, request: Request, pk: int):
        supervision = get_object_or_404(Supervision.objects, pk=pk)
        SupervisionService().verify(supervision)

        return Response(status=status.HTTP_200_OK)

    def clear_verification(self, request: Request, pk: int):
        supervision = get_object_or_404(Supervision.objects, pk=pk)
        SupervisionService().clear_verification(supervision)

        return Response(status=status.HTTP_200_OK)

    def delete_not_verified(self, request):
        deleted_entities_count, deleted_entities_dict = SupervisionService().delete_not_verified_supervisions()
        data = {
            "deleted_entities_count": deleted_entities_count,
            "deleted_entities": deleted_entities_dict,
        }
        return Response(data=data, status=status.HTTP_200_OK)

    def last_active_supervision(self, request):
        supervision = SupervisionService().get_user_last_active_supervision(request.user)
        if supervision:
            serializer = self.serializer_class(supervision)
            return Response(data=serializer.data, status=status.HTTP_200_OK)
        return Response(status=status.HTTP_204_NO_CONTENT)

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
    permission_classes = (IsSupervisor,)
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
    permission_classes = (IsSupervisor,)
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
    permission_classes = (IsSupervisor,)
    serializer_class = serializers.AnalyticsDetailsSerializer
    queryset = ActivityStatistics.objects.prefetch_related("comments")
    lookup_field = "pk"

    def get_serializer_class(self):
        if self.action == "retrieve":
            return serializers.AnalyticsDetailsSerializer

        elif self.action in ("partial_update", "update"):
            return serializers.AnalyticsUpdateSerializer

    def verify(self, request: Request, pk: int):
        activity_statistics = get_object_or_404(ActivityStatistics.objects, pk=pk)
        ActivityStatisticsService().verify(activity_statistics)

        return Response(status=status.HTTP_200_OK)

    def clear_verification(self, request: Request, pk: int):
        activity_statistics = get_object_or_404(ActivityStatistics.objects, pk=pk)
        ActivityStatisticsService().clear_verification(activity_statistics)

        return Response(status=status.HTTP_200_OK)
