from ej_conversations.tests.conftest import *
from ej_clusters.tests.conftest import *
from ej_activation.models import SegmentFilter


@pytest.fixture
def segmentFilter(db, conversation, clusterization, cluster, vote):
    clusterization.update_clusterization(force=True)
    segment = SegmentFilter(conversation=conversation, engagement_level=0.3, comments={})
    segment.save()
    segment.clusters.set([cluster])
    yield segment
    segment.delete()
