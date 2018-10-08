import logging
from datetime import datetime
from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth import get_user_model
from model_utils.models import TimeFramedModel
from polymorphic.models import PolymorphicModel
from django.core.validators import validate_comma_separated_integer_list

from ej_conversations.fields import UserRef, CommentRef
from .functions import promote_comment

NO_PROMOTE_MSG = _('user does not have the right to promote this comment')
log = logging.getLogger('ej')


class CommentPromotion(TimeFramedModel):
    """
    Describes the act of one user promoting an specific comment.

    Better use the :func:`ej_powers.promote_comment` function instead of
    creating instances of this class manually.
    """
    comment = CommentRef()
    promoter = UserRef(related_name='promotions')
    users = models.ManyToManyField(
        get_user_model(),
        related_name='see_promotions',
    )
    is_expired = property(lambda self: self.end < datetime.now())

    def recycle(self):
        """
        Remove itself from database if promotion is expired.
        """
        if self.is_expired:
            self.delete()
            log.info(f'Removed expired promotion for {self.comment} comment.')


class GivenPower(TimeFramedModel, PolymorphicModel):
    """
    Concede a power to some specific user.

    This object is stored while power is still not in effect.

    Relation with other users are stored in a CommaSeparatedIntegerField blob
    to make DB usage more efficient.
    """
    user = UserRef()
    data = models.CharField(validators=[validate_comma_separated_integer_list], max_length=10000)
    is_exhausted = models.BooleanField(default=False)
    is_expired = property(lambda self: self.end < datetime.now())

    def use_power(self, **kwargs):
        raise NotImplementedError('implement in subclass')


class GivenBridgePower(GivenPower):
    """
    Given "Conversation bridge" power.
    """

    class Meta:
        proxy = True

    def get_affected_users(self):
        """
        Return queryset with all affected users.
        """
        user_ids = self.data
        return get_user_model().objects.filter(id__in=user_ids)

    def use_power(self, comment):
        return promote_comment(comment,
                               author=self.user,
                               users=self.affected_users(),
                               expires=self.end)


class GivenMinorityPower(GivenPower):
    """
    Given "Minority activist" power.
    """

    class Meta:
        proxy = True

    get_affected_users = GivenBridgePower.get_affected_users
    use_power = GivenBridgePower.use_power
