from django.urls import path

from . import views

urlpatterns = [
    path("organizations/", views.OrganizationListView.as_view({"get": "list"}), name="organization_list"),
    path("organizations/<int:pk>/", views.OrganizationListView.as_view({"get": "retrieve"}), name="organization_detail"),

    path("classifiers/", views.ClassifierListView.as_view({"get": "list"}), name="organization_list"),
    path("classifiers/<int:pk>/", views.ClassifierListView.as_view({"get": "retrieve"}), name="organization_detail"),
]
