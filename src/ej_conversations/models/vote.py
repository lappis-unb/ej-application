from django.conf import settings
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _

from boogie import models
from boogie.fields import EnumField
from .vote_queryset import VoteQuerySet
from ..enums import Choice

VOTE_ERROR_MESSAGE = _("vote should be one of 'agree', 'disagree' or 'skip', got {value}")
VOTING_ERROR = lambda value: ValueError(VOTE_ERROR_MESSAGE.format(value=value))
VOTE_NAMES = {Choice.AGREE: "agree", Choice.DISAGREE: "disagree", Choice.SKIP: "skip"}
VOTE_VALUES = {v: k for k, v in VOTE_NAMES.items()}


class VoteChannels:
    TELEGRAM = "telegram"
    WHATSAPP = "whatsapp"
    OPINION_COMPONENT = "opinion_component"
    RASA_WEBCHAT = "socketio"
    RASAX = "rasa"
    UNKNOWN = "unknown"
    EJ = "ej"

    @staticmethod
    def choices():
        return [
            (VoteChannels.TELEGRAM, "Telegram"),
            (VoteChannels.WHATSAPP, "Whatsapp"),
            (VoteChannels.RASAX, "RASAX"),
            (VoteChannels.OPINION_COMPONENT, _("Opinion Component")),
            (VoteChannels.RASA_WEBCHAT, _("Rasa webchat")),
            (VoteChannels.EJ, _("EJ")),
            (VoteChannels.UNKNOWN, _("Unknown")),
        ]


class Vote(models.Model):
    """
    A single vote cast for a comment.
    """

    author = models.ForeignKey(
        settings.AUTH_USER_MODEL, related_name="votes", on_delete=models.PROTECT
    )
    comment = models.ForeignKey("Comment", related_name="votes", on_delete=models.CASCADE)
    choice = EnumField(Choice, _("Choice"), help_text=_("Agree, disagree or skip"))
    created = models.DateTimeField(_("Created at"), auto_now_add=True)
    channel = models.CharField(
        _("Channel"),
        max_length=50,
        blank=False,
        help_text=_("From which EJ channel the vote comes from"),
        choices=VoteChannels.choices(),
        default=VoteChannels.UNKNOWN,
    )
    objects = VoteQuerySet.as_manager()

    class Meta:
        unique_together = ("author", "comment")
        ordering = ["id"]

    def __str__(self):
        comment = truncate(self.comment.content, 40)
        return f"{self.author} - {self.choice.name} ({comment})"

    def clean(self, *args, **kwargs):
        if self.comment.is_pending:
            msg = _("non-moderated comments cannot receive votes")
            raise ValidationError(msg)


#
# UTILITY FUNCTIONS
#
def normalize_choice(value):
    """
    Normalize numeric and string values to the correct vote value that
    should be stored in the database.
    """
    if value in VOTE_NAMES:
        return value
    try:
        return VOTE_VALUES[value]
    except KeyError:
        raise VOTING_ERROR(value)


def truncate(st, size):
    if len(st) > size - 2:
        return st[: size - 3] + "..."
    return st
