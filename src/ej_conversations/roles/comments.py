from django.urls import reverse
from django.utils.translation import gettext_lazy as _

from hyperpython import a
from hyperpython.django import csrf_input

from ej.roles import with_template
from .. import models
from ..enums import RejectionReason
from ..models import Comment


@with_template(Comment, role="card")
def comment_card(comment: Comment, request=None, target=None, show_actions=None, message=None, **kwargs):
    """
    Render comment information inside a comment card.
    """

    user = getattr(request, "user", None)
    show_actions = getattr(user, "is_authenticated", False)

    if show_actions:
        login_anchor = None
    else:
        login = reverse("auth:login")
        login_anchor = a(_("login"), href=f"{login}?next={comment.conversation.get_absolute_url()}")

    badge = ""

    buttons = {
        "disagree": ("fa-times", "text-negative", _("Disagree")),
        "skip": ("fa-arrow-right", "text-black", _("Skip")),
        "agree": ("fa-check", "text-positive", _("Agree")),
    }

    if user and user.is_anonymous:
        show_actions, message = True, None

    return {
        "author": comment.author.username,
        "comment": comment,
        "show_actions": show_actions,
        "message": message,
        "csrf_input": csrf_input(request),
        "buttons": buttons,
        "login_anchor": login_anchor,
        "target": target,
        "badge": badge,
        **kwargs,
    }


@with_template(Comment, role="moderate")
def comment_moderate(comment: Comment, request=None, **kwargs):
    """
    Render a comment inside a moderation card.
    """

    moderator = getattr(comment.moderator, "name", None)
    return {
        "created": comment.created,
        "author": comment.author_name,
        "text": comment.content,
        "moderator": moderator,
    }


@with_template(Comment, role="reject-reason")
def comment_reject_reason(comment: Comment, **kwargs):
    """
    Show reject reason for each comment.
    """

    rejection_reason = comment.rejection_reason_text
    if comment.status != comment.STATUS.rejected:
        rejection_reason = None
    elif comment.rejection_reason != RejectionReason.USER_PROVIDED:
        rejection_reason = comment.rejection_reason.description

    return {
        "comment": comment,
        "conversation_url": comment.conversation.get_absolute_url(),
        "status": comment.status,
        "status_name": dict(models.Comment.STATUS)[comment.status].capitalize(),
        "rejection_reason": rejection_reason,
    }


@with_template(Comment, role="summary")
def comment_summary(comment: Comment, **kwargs):
    """
    Show comment summary.
    """
    status_icon = {"approved": "thumbtack", "rejected": "ban", "pending": "clock"}

    return {
        "created": comment.created,
        "comment_url": comment.comment_url(),
        "text": comment.content,
        "status": Comment.STATUS[comment.status],
        "status_icon": status_icon.get(comment.status),
        "conversation": comment.conversation,
    }


@with_template(Comment, role="stats", template="ej/role/voting-stats.jinja2")
def comment_stats(comment: Comment, request=None):
    return {
        "agree": comment.agree_count,
        "skip": comment.skip_count,
        "disagree": comment.disagree_count,
        "request": request,
    }
