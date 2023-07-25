from django.urls import path
from . import views
from .views import PublicConversationView

app_name = "ej_conversations"
conversation_url = "<int:conversation_id>/<slug:slug>/"

urlpatterns = [
    path(
        "",
        PublicConversationView.as_view(),
        name="list",
    ),
]
