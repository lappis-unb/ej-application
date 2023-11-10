from ej_activation.models import SegmentFilter
from ej_conversations.models.comment import Comment
from ej_users.models import User


def test_segment_filter_instance(db, conversation, cluster):
    segment = SegmentFilter(conversation=conversation, engagement_level=0.3, comments={})
    # to set many to many, we need to save segment first.
    segment.save()
    segment.clusters.set([cluster])
    assert segment.engagement_level == 0.3
    assert list(segment.clusters) == [cluster]
    assert segment.comments == {}


def test_get_clusters_by_name(db, conversation, cluster):
    segment_filter = SegmentFilter(conversation=conversation, engagement_level=0.3, comments={})
    segment_filter.save()
    segment_filter.clusters.set([cluster])
    clusters = segment_filter.get_clusters_by_id([str(cluster.id)])
    assert clusters
    assert clusters[0].name == cluster.name


def test_get_clusters_by_name_empty(db, conversation, cluster):
    segment_filter = SegmentFilter(conversation=conversation, engagement_level=0.3, comments={})
    segment_filter.save()
    segment_filter.clusters.set([cluster])
    clusters = segment_filter.get_clusters_by_id([])
    assert clusters == []


def test_filter_by_clusters(db, conversation, clusterization, cluster, vote):
    clusterization.update_clusterization(force=True)
    segment = SegmentFilter(conversation=conversation, engagement_level=0.3, comments={})
    segment.save()
    segment.clusters.set([cluster])
    queryset = segment._filter_by_clusters()
    assert queryset
    assert queryset[0]


def test_filter_by_empty_clusters(db, conversation, vote):
    segment = SegmentFilter(conversation=conversation, engagement_level=0.3, comments={})
    segment.save()
    queryset = segment._filter_by_clusters()
    assert queryset
    assert queryset[0]


def test_filter_by_empty_conversation(db, conversation):
    segment = SegmentFilter(conversation=conversation, engagement_level=0.3, comments={})
    segment.save()
    queryset = segment._filter_by_clusters()
    assert len(queryset) == 0


def test_filter(db, segmentFilter):
    queryset = segmentFilter.filter()
    assert queryset
    assert type(queryset[0]) == User


def test_filter_by_comments_with_agree(db, segmentFilter: SegmentFilter, comment: Comment):
    comments = {comment.id: "agree"}
    segmentFilter.comments = comments
    segmentFilter.save()
    queryset = segmentFilter.filter()
    assert queryset
    assert type(queryset[0]) == User


def test_filter_by_comments_with_disagree(db, segmentFilter: SegmentFilter, comment: Comment):
    comments = {comment.id: "disagree"}
    segmentFilter.comments = comments
    segmentFilter.save()
    queryset = segmentFilter.filter()
    assert len(queryset) == 0


def test_unselect_comment(db, segmentFilter: SegmentFilter, comment: Comment):
    segmentFilter.remove_or_update_comment(comment.id, "agree")
    segmentFilter.save()
    queryset = segmentFilter.filter()
    assert type(queryset[0]) == User
