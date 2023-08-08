from ej_conversations.tests.conftest import *
from ej_conversations.enums import Choice
from ej_clusters.models.clusterization import Clusterization
from ej_clusters.models.cluster import Cluster
from ej_clusters.models.stereotype import Stereotype
from ej_clusters.models.stereotype_vote import StereotypeVote
import pytest


@pytest.fixture
def stereotype(db, comment, user):
    stereotype = Stereotype.objects.create(name="stereotype", owner=user)
    stereotype_vote = StereotypeVote.objects.create(author=stereotype, comment=comment, choice=Choice.AGREE)
    return stereotype


@pytest.fixture
def clusterization(db, conversation):
    clusterization = Clusterization.objects.create(conversation=conversation)
    return clusterization


@pytest.fixture
def cluster(db, clusterization, stereotype):
    cluster = Cluster.objects.create(clusterization=clusterization, name="My Cluster")
    cluster.stereotypes.add(stereotype)
    cluster.save()
    return cluster
