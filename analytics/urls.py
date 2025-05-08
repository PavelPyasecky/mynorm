from django.urls import path

from . import views

urlpatterns = [
    path("", views.SupervisionViewSet.as_view({"post": "create", "get": "list"}), name="supervision"),
    path("<int:pk>/", views.SupervisionViewSet.as_view({"get": "retrieve"}), name="supervision_detail"),
    path("<int:pk>/finish/", views.SupervisionViewSet.as_view({'post': 'finish'}), name="supervision_detail"),
    path("<int:pk>/failure/", views.SupervisionViewSet.as_view({'post': 'failure'}), name="supervision_detail"),
    path("analytics/<int:analytics_id>/comment/", views.AnalyticsCommentView.as_view({"post": "create"}),
         name="analytics_comment"),
    path("<int:pk>/analytics/", views.AnalyticsListView.as_view({"get": "list"}), name="analytics"),
    path("<int:pk>/activity/", views.AnalyticsCreateViewSet.as_view({'post': 'create'}), name="analytics_create"),
]