from django.urls import path
from ..views import stereotypes

app_name = "ej_cluster"

urlpatterns = [
    path(
        "",
        stereotypes.StereotypeListView.as_view(),
        name="list",
    ),
    path(
        "add/",
        stereotypes.StereotypeCreateView.as_view(),
        name="create",
    ),
    path(
        "<int:pk>/edit/",
        stereotypes.StereotypeEditView.as_view(),
        name="edit",
    ),
]
