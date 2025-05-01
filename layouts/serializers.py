from rest_framework import serializers

from layouts.models import Layout, ActivityGroup, Activity


class ActivitySerializer(serializers.ModelSerializer):
    class Meta:
        model = Activity
        fields = ('id', 'name')


class ActivityGroupSerializer(serializers.ModelSerializer):
    activities = ActivitySerializer(many=True)
    class Meta:
        model = ActivityGroup
        fields = ('id', 'name', 'activities')


class LayoutSerializer(serializers.ModelSerializer):
    activity_groups = ActivityGroupSerializer(many=True)
    class Meta:
        model = Layout
        fields = ('id', 'organization', 'classifier', 'activity_groups')
