import json

from django.contrib.gis.geos import Point
from rest_framework import serializers
from rest_framework_gis.fields import GeometryField
from rest_framework_gis.serializers import GeoModelSerializer

from analytics.models import (
    ActivityStatistics,
    Supervision,
    Comment,
    CommentFiles,
    Failure,
)
from core.models import Organization
from core.serializers import ClassifierSerializer
from layouts.models import Activity
from users.models import User


class OrganizationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Organization
        fields = ("id", "name")


class UserSerializer(serializers.ModelSerializer):
    classifier = ClassifierSerializer(read_only=True)

    class Meta:
        model = User
        fields = ("id", "username", "first_name", "last_name", "email", "classifier")


class CommentFileSerializer(serializers.ModelSerializer):
    class Meta:
        model = CommentFiles
        fields = ("id", "file")


class CommentSerializer(GeoModelSerializer):
    files = CommentFileSerializer(many=True, read_only=True)
    coordinates = GeometryField(required=False)

    class Meta:
        model = Comment
        geo_field = 'coordinates'
        fields = ("id", "text", "coordinates", "map_url", "files")

    def to_representation(self, instance):
        """
        Convert Point object to GeoJSON format
        """
        representation = super().to_representation(instance)

        if isinstance(representation.get('coordinates'), dict):
            return representation

        if hasattr(instance, 'coordinates') and instance.coordinates:
            representation['coordinates'] = {
                'type': 'Point',
                'coordinates': [
                    instance.coordinates.x,
                    instance.coordinates.y
                ]
            }
        return representation


class CommentCreateSerializer(CommentSerializer):
    files = serializers.ListField(
        child=serializers.FileField(required=False),
        allow_empty=True,
        required=False,

    )

    class Meta:
        model = Comment
        geo_field = 'coordinates'
        fields = ("id", "text", "coordinates", "files")
        extra_kwargs = {
            "text": {"default": "", "allow_null": False},
        }

    def validate_coordinates(self, value):
        """Ensure coordinates are properly formatted"""
        if isinstance(value, str):
            try:
                value = json.loads(value)
            except json.JSONDecodeError:
                raise serializers.ValidationError("Invalid JSON string for coordinates")

        if isinstance(value, list):
            if len(value) != 2:
                raise serializers.ValidationError("Coordinates must be an array of [longitude, latitude]")
            value = {'type': 'Point', 'coordinates': value}

        if not isinstance(value, Point) and (not isinstance(value, dict) or 'coordinates' not in value):
            raise serializers.ValidationError("Coordinates must be in GeoJSON format")

        return value


class SupervisionSerializer(serializers.ModelSerializer):
    worker = UserSerializer(read_only=True)
    user = UserSerializer(read_only=True)
    organization = OrganizationSerializer(read_only=True)

    class Meta:
        model = Supervision
        fields = (
            "id",
            "worker",
            "organization",
            "user",
            "start_date",
            "end_date",
            "delta",
            "admin_comment",
        )
        extra_kwargs = {
            "start_date": {"read_only": True},
            "end_date": {"read_only": True},
        }


class SupervisionLiteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Supervision
        fields = (
            "id",
            "worker",
            "organization",
            "user",
            "start_date",
            "end_date",
        )
        extra_kwargs = {
            "start_date": {"read_only": True},
            "end_date": {"read_only": True},
        }


class SupervisionCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Supervision
        fields = (
            "id",
            "worker",
            "organization",
            "user",
            "start_date",
            "end_date",
        )
        extra_kwargs = {
            "start_date": {"read_only": True},
            "end_date": {"read_only": True},
            "user": {"read_only": True},
        }

    def create(self, validated_data):
        validated_data["user"] = self.context["request"].user
        validated_data["created_by"] = self.context["request"].user
        validated_data["updated_by"] = self.context["request"].user
        return super().create(validated_data)


class SupervisionUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Supervision
        fields = (
            "id",
            "worker",
            "organization",
            "user",
            "start_date",
            "end_date",
            "admin_comment",
        )
        extra_kwargs = {
            "worker": {"required": False},
            "user": {"required": False},
            "admin_comment": {"required": False, "allow_blank": True},
        }


class AnalyticsUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = ActivityStatistics
        fields = (
            "id",
            "activity",
            "supervision",
            "failure",
            "start_date",
            "end_date",
            "delta",
            "admin_comment",
        )
        extra_kwargs = {
            "delta": {"read_only": True},
            "admin_comment": {"required": False, "allow_blank": True},
        }


class AnalyticsCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = ActivityStatistics
        fields = ("id", "activity", "start_date", "end_date")
        extra_kwargs = {
            "start_date": {"required": False},
            "end_date": {"required": False},
            "comment": {"required": False},
        }

    def create(self, validated_data):
        validated_data["created_by"] = self.context["request"].user
        validated_data["updated_by"] = self.context["request"].user
        return super().create(validated_data)


class FailureSerializer(serializers.ModelSerializer):
    class Meta:
        model = Failure
        fields = ("id", "start_date", "end_date", "delta")
        extra_kwargs = {
            "delta": {"read_only": True},
        }


class ActivitySerializer(serializers.ModelSerializer):
    class Meta:
        model = Activity
        fields = (
            "id",
            "name",
            "planned_start_time",
            "planned_end_time",
            "planned_delta",
        )


class AnalyticsDetailsSerializer(serializers.ModelSerializer):
    activity = ActivitySerializer()
    supervision = SupervisionSerializer(read_only=True)
    failure = FailureSerializer(read_only=True)
    delta = serializers.CharField(read_only=True)
    comments = CommentSerializer(many=True, read_only=True)

    class Meta:
        model = ActivityStatistics
        fields = (
            "id",
            "activity",
            "supervision",
            "failure",
            "comments",
            "admin_comment",
            "start_date",
            "end_date",
            "delta",
            "verified",
            "verification_date",
        )


class AnalyticsDetailsLiteSerializer(AnalyticsDetailsSerializer):
    supervision = SupervisionLiteSerializer(read_only=True)

    class Meta(AnalyticsDetailsSerializer.Meta):
        pass


class SupervisionListSerializer(serializers.ModelSerializer):
    worker = UserSerializer(read_only=True)
    user = UserSerializer(read_only=True)
    organization = OrganizationSerializer(read_only=True)
    analytics = AnalyticsDetailsLiteSerializer(source="statistics", many=True, read_only=True)
    display_total_failure_delta = serializers.CharField(read_only=True)
    overtime_activities_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = Supervision
        fields = (
            "id",
            "worker",
            "organization",
            "user",
            "start_date",
            "end_date",
            "planned_start_time",
            "planned_end_time",
            "delta",
            "planned_delta",
            "overtime_activities_count",
            "display_total_failure_delta",
            "validity",
            "verified",
            "verification_date",
            "admin_comment",
            "analytics",
        )
        extra_kwargs = {
            "start_date": {"read_only": True},
            "end_date": {"read_only": True},
        }
