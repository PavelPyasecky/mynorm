from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from app_settings.models import AppSetting


class AppSettingModelTest(TestCase):
    """Test cases for AppSetting singleton model."""
    
    def test_singleton_behavior(self):
        """Test that only one instance can exist."""
        # Create first instance
        app_setting1 = AppSetting.load()
        self.assertEqual(app_setting1.pk, 1)
        
        # Try to create another instance
        app_setting2 = AppSetting.load()
        self.assertEqual(app_setting2.pk, 1)
        self.assertEqual(app_setting1, app_setting2)
        
        # Verify only one instance exists
        self.assertEqual(AppSetting.objects.count(), 1)
    
    def test_save_always_sets_pk_to_1(self):
        """Test that save always sets pk to 1."""
        app_setting = AppSetting.objects.create(
            hide_failure_btn=True,
            hide_info_btn=False
        )
        
        # Even if we try to set a different pk, it should be 1
        self.assertEqual(app_setting.pk, 1)
    
    def test_delete_prevention(self):
        """Test that delete is prevented."""
        app_setting = AppSetting.load()
        
        # Try to delete - should not work
        app_setting.delete()
        
        # Instance should still exist
        self.assertTrue(AppSetting.objects.filter(pk=1).exists())


class AppSettingAPITest(APITestCase):
    """Test cases for AppSetting API endpoints."""
    
    def setUp(self):
        """Set up test data."""
        self.app_setting = AppSetting.load()
        self.app_setting.hide_failure_btn = True
        self.app_setting.hide_info_btn = False
        self.app_setting.save()
    
    def test_get_app_setting_detail(self):
        """Test getting specific app setting."""
        url = reverse('app-settings-detail', kwargs={'pk': 1})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['hide_failure_btn'], True)
        self.assertEqual(response.data['hide_info_btn'], False)
    
    def test_get_current_settings(self):
        """Test getting current settings via custom action."""
        url = reverse('app-settings-current')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['hide_failure_btn'], True)
        self.assertEqual(response.data['hide_info_btn'], False)
    
    def test_update_current_settings(self):
        """Test updating current settings via custom action."""
        url = reverse('app-settings-update-current')
        data = {
            'hide_failure_btn': False,
            'hide_info_btn': True
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Verify the update
        self.app_setting.refresh_from_db()
        self.assertEqual(self.app_setting.hide_failure_btn, False)
        self.assertEqual(self.app_setting.hide_info_btn, True)
    
    def test_singleton_creation_via_api(self):
        """Test that API creates singleton if none exist."""
        # Delete existing settings
        AppSetting.objects.all().delete()
        
        url = reverse('app-settings-current')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Verify a new instance was created with pk=1
        self.assertEqual(AppSetting.objects.count(), 1)
        self.assertTrue(AppSetting.objects.filter(pk=1).exists())
    
    def test_update_creates_singleton_if_none_exist(self):
        """Test that update creates singleton if none exist."""
        # Delete existing settings
        AppSetting.objects.all().delete()
        
        url = reverse('app-settings-update-current')
        data = {
            'hide_failure_btn': True,
            'hide_info_btn': True
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Verify singleton was created
        self.assertEqual(AppSetting.objects.count(), 1)
        app_setting = AppSetting.objects.get(pk=1)
        self.assertEqual(app_setting.hide_failure_btn, True)
        self.assertEqual(app_setting.hide_info_btn, True)
