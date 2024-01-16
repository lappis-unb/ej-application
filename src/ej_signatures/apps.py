from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class EjSignaturesConfig(AppConfig):
    name = "ej_signatures"
    verbose_name = _("Signatures")
    rules = None
    api = None
    roles = None

    def ready(self):
        import ej_conversations.views as ej_conversations_views

        ej_conversations_views.BoardConversationsView.template_name = (
            "ej_signatures/board-conversations-list.jinja2"
        )
