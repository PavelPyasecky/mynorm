from rest_framework import status
from rest_framework.generics import get_object_or_404
from rest_framework.mixins import ListModelMixin, CreateModelMixin, RetrieveModelMixin
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet

from analytics import serializers, exceptions
from analytics.models import ActivityStatistics, Supervision, Comment, CommentFiles, CommentImage
from analytics.services import SupervisionService, FailureService, ActivityStatisticsService
from core.permissions import IsSupervisor


class AnalyticsListView(ListModelMixin, GenericViewSet):
    permission_classes = (IsSupervisor,)
    serializer_class = serializers.AnalyticsSerializer
    queryset = ActivityStatistics.objects.all()
    ordering = ['start_date']

    def get_queryset(self):
        supervision_id = self.kwargs.get('pk')
        get_object_or_404(Supervision, id=supervision_id)
        return self.queryset.filter(supervision_id=supervision_id)


class AnalyticsCreateViewSet(CreateModelMixin, GenericViewSet):
    permission_classes = (IsSupervisor,)
    serializer_class = serializers.ActivityStatisticsCreateSerializer
    queryset = ActivityStatistics.objects.all()

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        supervision_id = self.kwargs.get('pk')
        get_object_or_404(Supervision, id=supervision_id)
        serializer.validated_data['supervision_id'] = supervision_id

        previous_activity_statistic = ActivityStatistics.objects.filter(supervision_id=supervision_id,
                                                                        end_date__isnull=True).last()
        new_activity = serializer.validated_data['activity']
        activity_statistic = ActivityStatisticsService().start_activity(serializer.validated_data,
                                                                        previous_activity_statistic,
                                                                        new_activity)
        serializer = self.get_serializer(activity_statistic)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class SupervisionViewSet(RetrieveModelMixin, CreateModelMixin, ListModelMixin, GenericViewSet):
    permission_classes = (IsSupervisor,)
    serializer_class = serializers.SupervisionSerializer
    queryset = Supervision.objects.all()

    def get_serializer_class(self):
        if self.action in ('list', 'retrieve'):
            return serializers.SupervisionSerializer
        elif self.action == 'create':
            return serializers.SupervisionCreateSerializer

    def finish(self, request: Request, pk: int):
        supervision = get_object_or_404(Supervision.objects, pk=pk)
        SupervisionService.finish_supervision(supervision)

        return Response(status=status.HTTP_200_OK)


class AnalyticsCommentView(CreateModelMixin, GenericViewSet):
    permission_classes = (IsSupervisor,)
    serializer_class = serializers.CommentCreateSerializer
    queryset = Comment.objects.all()
    lookup_field = 'analytics_id'

    def perform_create(self, serializer):
        activity_statistics_id = self.kwargs.get('analytics_id')

        text = serializer.validated_data.get('text')
        images = serializer.validated_data.get('images')
        files = serializer.validated_data.get('files')

        if text or images or files:
            comment = Comment.objects.create(activity_statistics_id=activity_statistics_id, text=text,
                                             created_by=self.request.user, updated_by=self.request.user)

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


class AnalyticsFailureView(GenericViewSet):
    permission_classes = (IsSupervisor,)
    serializer_class = serializers.FailureSerializer
    queryset = Comment.objects.all()
    lookup_field = 'analytics_id'

    def start_failure(self, request, *args, **kwargs):
        activity_statistics_id = self.kwargs.get('analytics_id')
        activity_statistics = get_object_or_404(ActivityStatistics, id=activity_statistics_id)

        failure = FailureService.create_failure(activity_statistics)

        serializer = self.get_serializer(failure)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def finish_failure(self, request, *args, **kwargs):
        activity_statistics_id = self.kwargs.get('analytics_id')
        activity_statistics = get_object_or_404(ActivityStatistics, id=activity_statistics_id)

        failure = FailureService.finish_failure(activity_statistics)

        serializer = self.get_serializer(failure)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
