from rest_framework import serializers

from core.models import Organization, Classifier


class OrganizationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Organization
        fields = ("id", "name")


class ClassifierSerializer(serializers.ModelSerializer):
    class Meta:
        model = Classifier
        fields = ("id", "code", "name")
