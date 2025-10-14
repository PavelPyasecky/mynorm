from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters
from rest_framework.mixins import ListModelMixin, RetrieveModelMixin
from rest_framework.viewsets import GenericViewSet

from core.permissions import CustomDjangoModelPermissions
from users import serializers
from users.filters import UserFilter
from users.models import User


class UserListView(ListModelMixin, RetrieveModelMixin, GenericViewSet):
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
