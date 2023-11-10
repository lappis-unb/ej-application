from django.apps import AppConfig
from django.urls import reverse
from django.utils.translation import gettext_lazy as _


class EjActivationConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "ej_activation"

    def customize_menu(self, conversation):
        """
        customize_menu injects links on conversation menu-detail template.
        """
        return {
            "title": _("Activation"),
            "links": [
                {
                    "a": reverse(
                        "activation:index",
                        kwargs={
                            "board_slug": conversation.board.slug,
                            "slug": conversation.slug,
                            "conversation_id": conversation.id,
                        },
                    ),
                    "text": _("Public segmentation"),
                }
            ],
        }
