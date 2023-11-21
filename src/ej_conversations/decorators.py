from ej_tools.tools import BotsTool
from ej_users.models import SignatureFactory, User
from ej_conversations.models.vote import VoteChannels
from rest_framework.exceptions import PermissionDenied
from django.utils.translation import gettext_lazy as _
from django.http import HttpResponse


TOOLS_CHANNEL = {
    "socketio": (_("Opinion Bots"), "webchat"),
    "telegram": (_("Opinion Bots"), "telegram"),
    "twilio": (_("Opinion Bots"), "whatsapp"),
    "opinion_component": (_("Opinion component"),),
    "rocketchat": (_("Rocket.Chat"),),
    "unknown": (),
}


def bot_tool_is_active(bots_tool, tool_name):
    """
    checks if a certain type of bot (webchat, telegram, whatsapp) is active.
    """
    tool = getattr(bots_tool, tool_name)
    return tool.is_active


def conversation_can_receive_channel_vote(func):
    """
    Checks if conversation is allowed to receive votes from a given channel (tool).
    If  conversation author signature does not have permission, a 403 error is raised.
    """

    def wrapper_func(self, request, vote):
        if vote.channel == VoteChannels.UNKNOWN:
            raise PermissionDenied(
                {"message": "conversation author can not receive votes from an unknown tool"}
            )

        try:
            conversation = vote.comment.conversation
            author_signature = SignatureFactory.get_user_signature(conversation.author)
            tool_channel = TOOLS_CHANNEL[vote.channel]
            tool = author_signature.get_tool(tool_channel[0], conversation)
        except Exception:
            raise PermissionDenied({"message": f"{vote.channel} tool was not found"})

        if not tool.is_active:
            raise PermissionDenied(
                {"message": f"{vote.channel} is not available on conversation author signature"}
            )
        if type(tool) == BotsTool and not bot_tool_is_active(tool, tool_channel[1]):
            raise PermissionDenied(
                {"message": f"{vote.channel} is not available on conversation author signature"}
            )

        return func(self, request, vote)

    return wrapper_func


def user_can_post_anonymously(func):
    """
    user_can_post_anonymously checks if conversation was configured to accept
    anonymous votes.
    """

    def wrapper(self, request, conversation_id, slug, board_slug, *args, **kwargs):
        conversation = self.get_object()
        request.user = User.creates_from_request_session(conversation, request)
        redirect_url = ""
        if conversation.reaches_anonymous_particiption_limit(request.user):
            redirect_url = f"/register/?sessionKey={request.session.session_key}&next={request.path}"
        elif request.user.is_anonymous:
            redirect_url = f"/register/?next={request.path}"

        if redirect_url:
            """
            Participation page utilizes HTMX library to make backend AJAX requests.
            In order to make a redirect with HTMX,
            we need to include HX-Redirect header in the response.
            For more information, access https://htmx.org/reference/.
            """
            response = HttpResponse()
            response["HX-Redirect"] = redirect_url
            response.status_code = 302
            return response

        return func(self, request, conversation_id, slug, board_slug, *args, **kwargs)

    return wrapper


def create_session_key(func):
    """
    create_session_key check if request.session.session_key is empty.
    If so, creates it.
    """

    def wrapper(self, **kwargs):
        User.creates_request_session_key(self.request)
        return func(self)

    return wrapper
