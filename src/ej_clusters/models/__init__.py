from django.urls import reverse
from .cluster import Cluster
from .cluster_queryset import ClusterQuerySet, ClusterManager
from .clusterization import Clusterization
from .querysets import (
    ClusterizationQuerySet,
    ClusterizationManager,
    StereotypeVoteQuerySet,
    StereotypeQuerySet,
)
from .stereotype import Stereotype
from .stereotype_vote import StereotypeVote

#
# Patch conversation app keeping namespace clean.
#
_apply_patch = lambda f: f()


@_apply_patch
def _patch_conversation_app():
    from ej.components import register_menu
    from ej_conversations.models import Conversation
    from django.utils.translation import gettext as _
    from sidekick import delegate_to, lazy
    from hyperpython import a

    not_given = object()

    def get_clusterization(conversation, default=not_given):
        """
        Initialize a clusterization object for the given conversation, if it does
        not exist.
        """
        try:
            return conversation.clusterization
        except (AttributeError, Clusterization.DoesNotExist):
            if default is not_given:
                mgm, _ = Clusterization.objects.get_or_create(conversation=conversation)
                return mgm
            else:
                return default

    Conversation.get_clusterization = get_clusterization
    Conversation._clusterization = lazy(get_clusterization)
    Conversation.clusters = delegate_to("_clusterization")
