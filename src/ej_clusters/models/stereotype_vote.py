from boogie import models
from boogie.fields import EnumField
from django.utils.translation import gettext_lazy as _
from sidekick import alias

from ej_conversations.enums import Choice
from .querysets import StereotypeVoteQuerySet


class StereotypeVote(models.Model):
    """
    Similar to vote, but it is not associated with a comment.

    It forms a m2m relationship between Stereotypes and comments.
    """

    author = models.ForeignKey(
        "Stereotype", related_name="votes", on_delete=models.CASCADE
    )
    comment = models.ForeignKey(
        "ej_conversations.Comment",
        verbose_name=_("Comment"),
        related_name="stereotype_votes",
        on_delete=models.CASCADE,
    )
    choice = EnumField(Choice, _("Choice"))
    stereotype = alias("author")
    objects = StereotypeVoteQuerySet.as_manager()

    class Meta:
        unique_together = [("author", "comment")]
        app_label = 'ej_clusters' 

    def __str__(self):
        return f"StereotypeVote({self.author}, value={self.choice})"
