from django.shortcuts import render
from ej_signatures.services.slack import SlackService
from ej_boards.models import Board
from django.utils.translation import gettext_lazy as _

from django.views.generic import ListView
from ej_signatures.models import SignatureFactory
from typing import Any, Dict


class BoardConversationsView(ListView):
    template_name = "ej_signatures/board-conversations-list.jinja2"

    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
        user = self.request.user
        board_slug = self.kwargs.get("board_slug", None)
        board = Board.objects.get(slug=board_slug)
        user_signature = SignatureFactory.get_user_signature(user)
        max_conversation_per_user = user_signature.get_conversation_limit()
        user_boards = Board.objects.filter(owner=user)

        return {
            "conversations": self.get_queryset(),
            "title": _(board.title),
            "subtitle": _("Participate voting and creating comments!"),
            "conversations_limit": max_conversation_per_user,
            "board": board,
            "user_boards": user_boards,
        }


def list_view(request, board_slug):
    user = request.user
    signature = user.signature

    context = {
        "signature": signature,
        "success": False,
        "user_boards": Board.objects.filter(owner=user),
        "board_slug": board_slug,
    }

    return render(request, "ej_signatures/signatures-list.jinja2", context)


def upgrade(request, board_slug):
    if request.method != "POST":
        return list_view(request, board_slug)

    user = request.user

    slack = SlackService()
    slack.notify_request(request)

    context = {
        "signature": user.signature,
        "success": True,
        "user_boards": Board.objects.filter(owner=user),
        "board_slug": board_slug,
    }

    return render(request, "ej_signatures/signatures-list.jinja2", context)
