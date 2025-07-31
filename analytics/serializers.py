from rest_framework import serializers

from analytics.models import (
    ActivityStatistics,
    Supervision,
    Comment,
    CommentImage,
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


class CommentImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = CommentImage
        fields = ("id", "image")


class CommentFileSerializer(serializers.ModelSerializer):
    class Meta:
        model = CommentFiles
        fields = ("id", "file")


class CommentSerializer(serializers.ModelSerializer):
    images = CommentImageSerializer(many=True, read_only=True)
    files = CommentFileSerializer(many=True, read_only=True)

    class Meta:
        model = Comment
        fields = ("id", "text", "images", "files")


class CommentCreateSerializer(serializers.ModelSerializer):
    images = serializers.ListField(
        child=serializers.ImageField(required=False),
        allow_empty=True,
        required=False,
    )
    files = serializers.ListField(
        child=serializers.FileField(required=False),
        allow_empty=True,
        required=False,
    )

    class Meta:
        model = Comment
        fields = ("id", "text", "images", "files")
        extra_kwargs = {
            "text": {"required": False},
        }


class SupervisionSerializer(serializers.ModelSerializer):
    worker = UserSerializer(read_only=True)
    user = UserSerializer(read_only=True)
    comments = CommentSerializer(many=True, read_only=True)
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
            "comments",
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


class AnalyticsSerializer(serializers.ModelSerializer):
    activity_id = serializers.CharField(source="activity.id", read_only=True)
    activity_name = serializers.CharField(
        source="activity.name", read_only=True
    )
    supervision = SupervisionLiteSerializer(read_only=True)

    class Meta:
        model = ActivityStatistics
        fields = (
            "id",
            "activity_id",
            "activity_name",
            "supervision",
            "start_date",
            "end_date",
            "delta",
        )


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
        fields = ("id", "name",)


class AnalyticsDetailsSerializer(serializers.ModelSerializer):
    activity = ActivitySerializer(read_only=True)
    supervision = SupervisionSerializer(read_only=True)
    failure = FailureSerializer(read_only=True)
    delta = serializers.CharField(read_only=True)

    class Meta:
        model = ActivityStatistics
        fields = ("id", "activity", "supervision", "failure", "start_date", "end_date", "delta")
