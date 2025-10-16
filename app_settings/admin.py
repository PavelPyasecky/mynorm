from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from django.urls import reverse
from django.utils.html import format_html

from app_settings.models import AppSetting


@admin.register(AppSetting)
class AppSettingAdmin(admin.ModelAdmin):
    """
    Admin configuration for AppSetting singleton model.
    Provides a simple interface for managing application settings.
    """
    list_display = ('id', 'hide_failure_btn', 'hide_info_btn', 'actions_column')
    list_editable = ('hide_failure_btn', 'hide_info_btn')
    list_display_links = ('id',)
    
    fieldsets = (
        (_('Button Settings'), {
            'fields': ('hide_failure_btn', 'hide_info_btn'),
            'description': _('Configure which buttons should be hidden in the application.')
        }),
    )
    
    def actions_column(self, obj):
        """Custom column to show available actions."""
        if obj.pk:
            return format_html(
                '<a href="{}" class="button">' + _('Edit') + '</a>',
                reverse('admin:app_settings_appsetting_change', args=[obj.pk])
            )
        return '-'
    actions_column.short_description = _('Actions')
    
    def has_add_permission(self, request):
        """
        Only allow adding if no AppSetting instance exists.
        This ensures there's only one settings instance.
        """
        return not AppSetting.objects.exists()
    
    def has_delete_permission(self, request, obj=None):
        """
        Prevent deletion of the singleton instance.
        """
        return False
    
    def changelist_view(self, request, extra_context=None):
        """
        Customize the changelist to show singleton behavior.
        """
        extra_context = extra_context or {}
        extra_context['title'] = _('Application Settings')
        extra_context['subtitle'] = _('Manage global application settings')
        
        # Ensure singleton exists
        AppSetting.load()
        
        return super().changelist_view(request, extra_context)
    
    def get_queryset(self, request):
        """
        Always return the singleton instance.
        """
        return AppSetting.objects.filter(pk=1)
