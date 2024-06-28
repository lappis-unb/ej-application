from django.utils.translation import gettext_lazy as _
from django.db import models

from boogie.fields import IntEnum


class RejectionReason(IntEnum):
    """
    Possible rejection reasons for a comment.
    """

    USER_PROVIDED = 0, _("User provided")
    INCOMPLETE_TEXT = (10, _("Incomplete or incomprehensible text"))
    OFF_TOPIC = (20, _("Off-topic"))
    OFFENSIVE_LANGUAGE = (30, _("Offensive content or language"))
    DUPLICATED_COMMENT = (40, _("Duplicated content"))
    VIOLATE_TERMS_OF_SERVICE = (50, _("Violates terms of service of the platform"))


class Choice(models.IntegerChoices):
    """
    Options for a user vote.
    """

    SKIP = 0, _("Skip")
    AGREE = 1, _("Agree")
    DISAGREE = -1, _("Disagree")
