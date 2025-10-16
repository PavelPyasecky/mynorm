"""
URL configuration for config project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include
from drf_spectacular.views import SpectacularAPIView, SpectacularRedocView, SpectacularSwaggerView
from config.auth_views import (
    CustomTokenObtainPairView,
    CustomTokenRefreshView,
    CustomTokenVerifyView,
)
from config.health_views import health_check, docs_health_check


urlpatterns = [
    path("admin/", admin.site.urls),
    path("neste_admin/", include("nested_admin.urls")),
    path(
        "api/token/", CustomTokenObtainPairView.as_view(), name="token_obtain_pair"
    ),
    path(
        "api/token/refresh/", CustomTokenRefreshView.as_view(), name="token_refresh"
    ),
    path("api/token/verify/", CustomTokenVerifyView.as_view(), name="token_verify"),
    path("api/layouts/", include("layouts.urls")),
    path("api/supervisions/", include("analytics.urls")),
    path("api/users/", include("users.urls")),
    path("api/core/", include("core.urls")),
    path("api/app-settings/", include("app_settings.urls")),
    
    # Health checks
    path("api/health/", health_check, name="health_check"),
    path("api/docs/health/", docs_health_check, name="docs_health_check"),
    
    # API Documentation
    path("api/schema/", SpectacularAPIView.as_view(), name="schema"),
    path("api/docs/", SpectacularSwaggerView.as_view(url_name="schema"), name="swagger-ui"),
    path("api/redoc/", SpectacularRedocView.as_view(url_name="schema"), name="redoc"),
]

if settings.DEBUG:
    urlpatterns = urlpatterns + static(
        settings.MEDIA_URL, document_root=settings.MEDIA_ROOT
    )
