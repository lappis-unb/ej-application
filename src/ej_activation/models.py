from typing import List

from django.db import models
from ej_conversations.models.vote import normalize_choice
from ej_users.models import User
from src.ej_dataviz.utils import get_user_data


class SegmentFilter(models.Model):
    """
    SegmentFilter stores filters to segment conversation participants.
    Client can filter users using engagement_level, conversation clusters and conversation comments.
    """

    conversation = models.ForeignKey("ej_conversations.Conversation", on_delete=models.CASCADE)
    clusters = models.ManyToManyField("ej_clusters.Cluster")
    comments = models.JSONField()
    engagement_level = models.PositiveIntegerField(default=0)

    def filter(self):
        """
        filtering conversation participants based on clusters,
        engagement_level and comments.
        """
        queryset = self._filter_by_clusters()
        queryset = self._filter_by_engagement_level(queryset)
        return self._filter_by_comments(queryset)

    def _filter_by_clusters(self):
        """
        get conversation participants filtered by self.clusters
        """
        if not self.clusters.all():
            return self.conversation.users

        return User.objects.filter(clusters__id__in=[cluster.id for cluster in self.clusters.all()])

    def _filter_by_engagement_level(self, users_queryset):
        """
        get conversation participants filtered by self.engagement_level.
        """

        value = self.engagement_level / 100

        if value > 1 or value < 0:
            raise Exception("engagement_level must be between 0 and 100")

        df = get_user_data(self.conversation)
        participants = df[df["participation"] >= value]["email"]
        return users_queryset.filter(email__in=participants.tolist())

    def _filter_by_comments(self, users_queryset):
        """
        returns a list of users with voting equal to self.comments dictionary.
        """
        if self.comments == {}:
            return users_queryset
        for comment_id, choice in self.comments.items():
            users_queryset = users_queryset.filter(
                votes__comment__id=comment_id, votes__choice=normalize_choice(choice)
            )
        return users_queryset

    def get_clusters_by_id(self, clusters: List[str]):
        """
        receives a list of cluster ids and returns a list of cluster objects
        """
        if not clusters:
            return []
        return self.conversation.clusters.filter(id__in=clusters)

    def remove_or_update_comment(self, comment_id: int, new_choice: str):
        """
        removes comment_id from self.comments if choice already exists.
        updates self.comments with comment_id and choice if they do not already exists.
        """
        try:
            current_choice = self.comments[comment_id]
            if current_choice == new_choice:
                self.comments.pop(comment_id)
                return
        except Exception as e:
            pass
        self.comments.update({comment_id: new_choice})
