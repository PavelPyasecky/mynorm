"""
Utility functions for accessing application settings.
Provides easy access to the singleton AppSetting instance.
"""
from django.core.cache import cache
from django.conf import settings

from app_settings.models import AppSetting


def get_app_settings():
    """
    Get the application settings singleton instance.
    Uses caching for better performance.
    
    Returns:
        AppSetting: The singleton settings instance
    """
    cache_key = 'app_settings'
    app_settings = cache.get(cache_key)
    
    if app_settings is None:
        app_settings = AppSetting.load()
        # Cache for 5 minutes
        cache.set(cache_key, app_settings, 300)
    
    return app_settings


def get_setting(setting_name, default=None):
    """
    Get a specific setting value.
    
    Args:
        setting_name (str): The name of the setting to retrieve
        default: Default value if setting doesn't exist
        
    Returns:
        The setting value or default
    """
    try:
        app_settings = get_app_settings()
        return getattr(app_settings, setting_name, default)
    except Exception:
        return default


def clear_settings_cache():
    """
    Clear the settings cache.
    Call this after updating settings to ensure fresh data.
    """
    cache.delete('app_settings')


def should_hide_failure_button():
    """
    Check if the failure button should be hidden.
    
    Returns:
        bool: True if failure button should be hidden
    """
    return get_setting('hide_failure_btn', False)


def should_hide_info_button():
    """
    Check if the info button should be hidden.
    
    Returns:
        bool: True if info button should be hidden
    """
    return get_setting('hide_info_btn', False)
