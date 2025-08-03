from django.urls import path

from . import views

urlpatterns = [
    path(
        "",
        views.SupervisionViewSet.as_view({"post": "create", "get": "list"}),
        name="supervision",
    ),
    path(
        "<int:pk>/",
        views.SupervisionViewSet.as_view({"get": "retrieve"}),
        name="supervision_detail",
    ),
    path(
        "<int:pk>/finish/",
        views.SupervisionViewSet.as_view({"post": "finish"}),
        name="supervision_detail",
    ),
    path(
        "analytics/<int:pk>/",
        views.AnalyticsDetailsView.as_view({"get": "retrieve", "patch": "partial_update"}),
        name="analytics_details",
    ),
    path(
        "analytics/<int:analytics_id>/comment/",
        views.AnalyticsCommentView.as_view({"post": "create"}),
        name="analytics_comment",
    ),
    path(
        "analytics/comment/<int:pk>/",
        views.AnalyticsCommentView.as_view({"patch": "update"}),
        name="analytics_comment",
    ),
    path(
        "<int:supervision_id>/activity/<int:activity_id>/start-failure/",
        views.AnalyticsFailureView.as_view({"post": "start_failure"}),
        name="activity_start_failure",
    ),
    path(
        "<int:supervision_id>/activity/<int:activity_id>/finish-failure/",
        views.AnalyticsFailureView.as_view({"post": "finish_failure"}),
        name="activity_finish_failure",
    ),
    path(
        "<int:pk>/analytics/",
        views.AnalyticsListView.as_view({"get": "list"}),
        name="analytics",
    ),
    path(
        "<int:pk>/activity/",
        views.AnalyticsCreateViewSet.as_view({"post": "create"}),
        name="analytics_create",
    ),
]
