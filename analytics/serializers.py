from rest_framework import serializers

from analytics.models import ActivityStatistics, Supervision
from core.models import Organization
from users.models import User


class OrganizationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Organization
        fields = ('id', 'name')


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'username', 'first_name', 'last_name', 'email')


class SupervisionSerializer(serializers.ModelSerializer):
    worker = UserSerializer(read_only=True)
    user = UserSerializer(read_only=True)

    class Meta:
        model = Supervision
        fields = ('id', 'name', 'worker', 'organization', 'user', 'start_date', 'end_date')
        extra_kwargs = {
            "name": {"required": False},
            "start_date": {"read_only": True},
            "end_date": {"read_only": True},
        }


class SupervisionLiteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Supervision
        fields = ('id', 'name', 'worker', 'organization', 'user', 'start_date', 'end_date')
        extra_kwargs = {
            "name": {"required": False},
            "start_date": {"read_only": True},
            "end_date": {"read_only": True},
        }


class SupervisionCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Supervision
        fields = ('id', 'name', 'worker', 'organization', 'user', 'start_date', 'end_date')
        extra_kwargs = {
            "name": {"required": False},
            "start_date": {"read_only": True},
            "end_date": {"read_only": True},
        }

    def create(self, validated_data):
        validated_data['created_by'] = self.context['request'].user
        validated_data['updated_by'] = self.context['request'].user
        return super().create(validated_data)


class AnalyticsSerializer(serializers.ModelSerializer):
    activity_id = serializers.CharField(source='activity.id', read_only=True)
    activity_name = serializers.CharField(source='activity.name', read_only=True)
    supervision = SupervisionLiteSerializer(read_only=True)

    class Meta:
        model = ActivityStatistics
        fields = ('id', 'activity_id', 'activity_name', 'supervision', 'start_date', 'end_date', 'delta')


class ActivityStatisticsCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = ActivityStatistics
        fields = ('id', 'activity', 'start_date', 'end_date')
        extra_kwargs = {
            "start_date": {"read_only": True},
            "end_date": {"read_only": True},
        }

    def create(self, validated_data):
        validated_data['created_by'] = self.context['request'].user
        validated_data['updated_by'] = self.context['request'].user
        return super().create(validated_data)
