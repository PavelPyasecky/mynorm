from rest_framework import status
from rest_framework.generics import get_object_or_404
from rest_framework.mixins import ListModelMixin, CreateModelMixin, RetrieveModelMixin
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet

from analytics import serializers, exceptions
from analytics.models import ActivityStatistics, Supervision
from analytics.utils import deactivate_activity, finish_supervision, deactivate_activities, \
    finish_supervision_with_failure
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

    def perform_create(self, serializer):
        supervision_id = self.kwargs.get('pk')
        get_object_or_404(Supervision, id=supervision_id)
        serializer.validated_data['supervision_id'] = supervision_id

        previous_activity_statistic = ActivityStatistics.objects.filter(supervision_id=supervision_id,
                                                                        end_date__isnull=True).last()

        if previous_activity_statistic:
            if previous_activity_statistic.activity == serializer.validated_data['activity']:
                raise exceptions.ActivityAlreadyActivatedException()

            deactivate_activity(previous_activity_statistic)

        super().perform_create(serializer)


class SupervisionViewSet(RetrieveModelMixin, CreateModelMixin, ListModelMixin, GenericViewSet):
    permission_classes = (IsSupervisor,)
    serializer_class = serializers.SupervisionSerializer
    queryset = Supervision.objects.all()

    def get_serializer_class(self):
        if self.action == 'retrieve':
            return serializers.SupervisionSerializer
        elif self.action == 'create':
            return serializers.SupervisionCreateSerializer

    def finish(self, request: Request, pk: int):
        supervision = get_object_or_404(Supervision.objects, pk=pk)

        previous_activity_statistic = ActivityStatistics.objects.filter(supervision=supervision,
                                                                        end_date__isnull=True).last()
        if previous_activity_statistic:
            deactivate_activity(previous_activity_statistic)

        finish_supervision(supervision)

        return Response(status=status.HTTP_200_OK)

    def failure(self, request: Request, pk: int):
        supervision = get_object_or_404(Supervision.objects, pk=pk)

        previous_activities_statistic = ActivityStatistics.objects.filter(supervision=supervision,
                                                                        end_date__isnull=True)
        if previous_activities_statistic:
            deactivate_activities(previous_activities_statistic)

        finish_supervision_with_failure(supervision)

        return Response(status=status.HTTP_200_OK)
