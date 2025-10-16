from rest_framework import serializers

from app_settings.models import AppSetting


class AppSettingSerializer(serializers.ModelSerializer):
    class Meta:
        model = AppSetting
        fields = ("id", "hide_failure_btn", "hide_info_btn")
        read_only_fields = ("id",)
