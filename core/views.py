from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters
from rest_framework.mixins import ListModelMixin, RetrieveModelMixin
from rest_framework.viewsets import GenericViewSet

from core import serializers
from core.models import Organization, Classifier
from core.permissions import IsSupervisor, IsSupervisorGroup, CustomDjangoObjectPermissions


class OrganizationListView(ListModelMixin, RetrieveModelMixin, GenericViewSet):
    permission_classes = (CustomDjangoObjectPermissions,)
    serializer_class = serializers.OrganizationSerializer
    queryset = Organization.objects.all()

    filter_backends = [filters.SearchFilter, DjangoFilterBackend]
    search_fields = ("name",)


class ClassifierListView(ListModelMixin, RetrieveModelMixin, GenericViewSet):
    permission_classes = (CustomDjangoObjectPermissions,)
    serializer_class = serializers.ClassifierSerializer
    queryset = Classifier.objects.all()

    filter_backends = [filters.SearchFilter, DjangoFilterBackend]
    search_fields = (
        "code",
        "name",
    )
