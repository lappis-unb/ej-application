from django.urls import path
from .. import views_comments

app_name = "ej_conversations"

urlpatterns = [
    path(
        "<int:comment_id>-<hex_hash>/",
        views_comments.CommentDetailView.as_view(),
        name="detail",
    )
]
