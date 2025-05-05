from rest_framework import serializers

from gallery.models import ImageGallery
from layouts.models import Layout, ActivityGroup, Activity


class ImageGallerySerializer(serializers.ModelSerializer):
    url = serializers.ImageField(source='image', read_only=True)
    class Meta:
        model = ImageGallery
        fields = ('url',)


class ActivitySerializer(serializers.ModelSerializer):
    class Meta:
        model = Activity
        fields = ('id', 'name')


class ActivityGroupSerializer(serializers.ModelSerializer):
    activities = ActivitySerializer(many=True)
    image = ImageGallerySerializer(read_only=True)

    class Meta:
        model = ActivityGroup
        fields = ('id', 'name', 'image', 'column_number', 'activities')


class LayoutSerializer(serializers.ModelSerializer):
    activity_groups = ActivityGroupSerializer(many=True)
    class Meta:
        model = Layout
        fields = ('id', 'organization', 'classifier', 'activity_groups')
