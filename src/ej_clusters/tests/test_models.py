from ej_clusters.mommy_recipes import ClusterRecipes
from ej_clusters.models.cluster import Cluster
from ej_clusters.models.stereotype import Stereotype
from ej_conversations.models.vote import Vote
from ej_users.models import User


class TestClusterization(ClusterRecipes):
    def test_inject_clusters_related_manager_on_conversation(self, conversation_db):
        conversation_db.get_clusterization()
        assert hasattr(conversation_db.clusterization, "clusters")
        assert hasattr(conversation_db, "clusters")

    def test_clusterization_str_method(self, conversation_db):
        conversation_db.get_clusterization()
        clusterization = conversation_db.clusterization

        assert str(clusterization) == f"{conversation_db} (0 clusters)"
        assert (
            f"{clusterization.get_absolute_url()}"
            == f"{conversation_db.get_absolute_url()}clusters/"
        )


class TestCluster:
    def test_concat_statistics_to_dataframe(self, clusterization, cluster, vote):
        clusterization.update_clusterization(force=True)
        cluster_df = cluster.concat_statistics_to_dataframe()
        assert cluster_df.iloc[0]["group"] == cluster.name
        assert cluster_df["content"].any()
        assert cluster_df["author"].any()
        assert cluster_df["participation"].any()
        assert cluster_df["convergence"].any()
        assert cluster_df["agree"].any()
        assert cluster_df.iloc[0]["disagree"] == 0.0
        assert cluster_df.iloc[0]["skipped"] == 0.0
