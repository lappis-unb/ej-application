from django.urls import path
from . import views

app_name = "ej_activation"
app_url = "<slug:board_slug>/conversations/<int:conversation_id>/<slug:slug>/activation"

urlpatterns = [
    path(
        app_url,
        views.ActivationIndexView.as_view(),
        name="index",
    ),
    path(
        f"{app_url}/add",
        views.ActivationAddView.as_view(),
        name="add",
    ),
    path(
        f"{app_url}/<int:pk>",
        views.ActivationDetailView.as_view(),
        name="detail",
    ),
    path(
        f"{app_url}/<int:pk>/comments",
        views.CommentsFrameView.as_view(),
        name="comments",
    ),
    path(
        f"{app_url}/<int:pk>/engagement-level",
        views.EngagementFrameView.as_view(),
        name="engagement-level",
    ),
    path(
        f"{app_url}/<int:pk>/clusters",
        views.ClustersFrameView.as_view(),
        name="clusters",
    ),
    path(
        f"{app_url}/<int:pk>/export",
        views.ActivationExportView.as_view(),
        name="export",
    ),
]
