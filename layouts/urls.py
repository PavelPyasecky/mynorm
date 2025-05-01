from django.urls import path

from . import views

urlpatterns = [
    path("", views.LayoutViewSet.as_view({"get": "list"}), name="layout-list"),
]