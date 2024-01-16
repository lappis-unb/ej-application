from boogie import rules
from django.conf import settings
from ej_signatures.models import SignatureFactory


@rules.register_value("ej.board_conversation_limit")
def conversation_limit(user):
    user_limit = user.limit_board_conversations
    if user_limit != 0:
        return user_limit
    else:
        return getattr(settings, "EJ_BOARD_MAX_CONVERSATIONS", float("inf"))


@rules.register_perm("ej.can_add_conversation")
def can_add_conversation(user):
    """
    Check if user can add a conversation
    """
    # Creates a instance from user signature
    user_signature = SignatureFactory.get_user_signature(user)
    return user_signature.can_add_conversation()
