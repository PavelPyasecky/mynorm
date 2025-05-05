from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters
from rest_framework.mixins import ListModelMixin, RetrieveModelMixin
from rest_framework.viewsets import GenericViewSet

from core.permissions import IsSupervisor
from users import serializers
from users.filters import UserFilter
from users.models import User


class UserListView(ListModelMixin, RetrieveModelMixin, GenericViewSet):
    permission_classes = (IsSupervisor,)
    serializer_class = serializers.UserSerializer
    queryset = User.objects.all()

    filter_backends = [filters.SearchFilter, UserFilter, DjangoFilterBackend]
    filterset_fields = ('organization', 'classifier')
    search_fields = ['username', 'first_name', 'last_name']
