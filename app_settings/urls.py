from django.urls import path, include
from rest_framework.routers import DefaultRouter

from app_settings import views

router = DefaultRouter()
router.register('', views.AppSettingViewSet, basename='app-settings')

urlpatterns = [
    path('', include(router.urls)),
]
