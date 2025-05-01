from rest_framework.mixins import ListModelMixin
from rest_framework.viewsets import GenericViewSet

from core.permissions import IsSupervisor
from layouts import serializers
from layouts.models import Layout


class LayoutViewSet(ListModelMixin, GenericViewSet):
    permission_classes = (IsSupervisor, )
    serializer_class = serializers.LayoutSerializer
    queryset = Layout.objects.all().prefetch_related('activity_groups', 'activity_groups__activities')
