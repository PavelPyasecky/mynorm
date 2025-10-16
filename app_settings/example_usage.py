"""
Example usage of the AppSettings singleton pattern.

This file demonstrates how to use the application settings
throughout your Django application.
"""

from django.http import JsonResponse
from django.views import View
from rest_framework.decorators import api_view
from rest_framework.response import Response

from app_settings.utils import (
    get_app_settings,
    get_setting,
    should_hide_failure_button,
    should_hide_info_button,
    clear_settings_cache
)


# Example 1: Using in a Django view
class ExampleView(View):
    """Example view showing how to use settings."""
    
    def get(self, request):
        """Get view that uses settings."""
        # Get the full settings object
        settings = get_app_settings()
        
        # Or get specific settings
        hide_failure = should_hide_failure_button()
        hide_info = should_hide_info_button()
        
        return JsonResponse({
            'hide_failure_button': hide_failure,
            'hide_info_button': hide_info,
            'settings_id': settings.id
        })


# Example 2: Using in a DRF view
@api_view(['GET'])
def example_api_view(request):
    """Example API view using settings."""
    # Get specific setting values
    hide_failure = get_setting('hide_failure_btn', False)
    hide_info = get_setting('hide_info_btn', False)
    
    return Response({
        'settings': {
            'hide_failure_button': hide_failure,
            'hide_info_button': hide_info,
        }
    })


# Example 3: Using in a template context processor
def settings_context_processor(request):
    """Template context processor for settings."""
    return {
        'hide_failure_button': should_hide_failure_button(),
        'hide_info_button': should_hide_info_button(),
    }


# Example 4: Using in a model or service
class SomeService:
    """Example service that uses settings."""
    
    def get_available_actions(self):
        """Get available actions based on settings."""
        actions = []
        
        if not should_hide_failure_button():
            actions.append('failure_action')
        
        if not should_hide_info_button():
            actions.append('info_action')
        
        return actions


# Example 5: Updating settings programmatically
def update_settings_example():
    """Example of updating settings programmatically."""
    # Get the settings instance
    settings = get_app_settings()
    
    # Update settings
    settings.hide_failure_btn = True
    settings.hide_info_btn = False
    settings.save()
    
    # Clear cache to ensure fresh data
    clear_settings_cache()
    
    print("Settings updated successfully!")


# Example 6: Using in middleware
class SettingsMiddleware:
    """Example middleware that uses settings."""
    
    def __init__(self, get_response):
        self.get_response = get_response
    
    def __call__(self, request):
        # Add settings to request for easy access
        request.app_settings = get_app_settings()
        
        response = self.get_response(request)
        return response
