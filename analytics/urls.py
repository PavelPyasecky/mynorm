from django.urls import path

from . import views

urlpatterns = [
    path("", views.SupervisionViewSet.as_view({"post": "create", "get": "list"}), name="supervision"),
    path("<int:pk>/", views.SupervisionViewSet.as_view({"get": "retrieve"}), name="supervision_detail"),
    path("<int:pk>/finish/", views.SupervisionViewSet.as_view({'post': 'finish'}), name="supervision_detail"),
    path("analytics/<int:analytics_id>/comment/", views.AnalyticsCommentView.as_view({"post": "create"}),
         name="analytics_comment"),
    path("analytics/<int:analytics_id>/start-failure/", views.AnalyticsFailureView.as_view({"post": "start_failure"}),
         name="analytics_start_failure"),
    path("analytics/<int:analytics_id>/finish-failure/", views.AnalyticsFailureView.as_view({"post": "finish_failure"}),
         name="analytics_finish_failure"),
    path("<int:pk>/analytics/", views.AnalyticsListView.as_view({"get": "list"}), name="analytics"),
    path("<int:pk>/activity/", views.AnalyticsCreateViewSet.as_view({'post': 'create'}), name="analytics_create"),
]
