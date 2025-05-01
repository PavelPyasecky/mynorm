from django.urls import path

from . import views

urlpatterns = [
    path("", views.UserListView.as_view({"get": "list"}), name="user"),
    path("<int:pk>/", views.UserListView.as_view({"get": "retrieve"}), name="user_detail"),
]
