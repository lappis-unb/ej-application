import logging
import numpy as np
import pandas as pd
from collections import defaultdict, Counter

log = logging.getLogger("ej")

def compute_cluster_affinities(votes, distance=lambda x, y: np.sum(np.abs(x - y))):
    """
    Returns a dictionary mapping clusters to a list of affinities.

    Each affinity is another dictionary mapping clusters to the degree of
    affinity for the user in each other cluster.

    Args:
        votes (dataframe):
            A votes dataframe with users as rows and comments as columns. It
            must contain an extra column named 'cluster' indicating in which
            cluster each user is classified.

            Usually this data will come from a call to ``clusterization.clusters.votes_table()``
        distance (callable):
            Distance function.
    """
    # Normalize votes data except for the cluster column
    labels = votes["cluster"].copy()
    votes = votes.drop(columns=["cluster"])
    votes = (votes - votes.mean()) / (votes.std() + 1e-6)
    votes["cluster"] = labels

    # Compute centroids for each cluster
    centroids = votes.groupby("cluster").mean()
    clusters = votes["cluster"].values
    votes = votes.drop(columns=["cluster"]).values

    tol = 1e-12
    shapes = defaultdict(lambda: {"intersections": defaultdict(float), "size": 0})

    # Vectorized approach for computing distances and intersections
    for k, x in zip(clusters, votes):
        centroid_k = centroids.loc[k].values
        coords = x - centroid_k
        distance_k = distance(x, centroid_k)
        shape = shapes[int(k)]

        # Compute intersections with other centroids
        differences = centroids.values - centroid_k
        dists = np.array([distance(coords, diff) for diff in differences])
        positive_intersections = np.dot(coords, differences.T) > 0

        # Update size and intersections
        shape["size"] += 1
        for k_, valid in enumerate(positive_intersections):
            if k_ != k and valid:
                shape["intersections"][int(centroids.index[k_])] += distance_k / (dists[k_] + tol) / 2

    return dict(shapes)

def summarize_affinities(affinities):
    """
    Process the result of :func:`compute_cluster_affinities`
    and returns a list of summaries for each cluster/intersection. This data
    is exposed in the /api/v1/clusterizations/<id>/affinities/ as:
    [{'sets': [1, 2], 'size': 3.14},
     {'sets': [1],    'size': 42},
     {'sets': [2],    'size': 10}]
    """
    intersections = Counter()
    counts = Counter()

    for k, data in affinities.items():
        counts[k] += data["size"]
        for k_, frac in data["intersections"].items():
            if k != k_:
                intersections[k, k_] += frac

    # Eliminate duplicate intersections
    for (k, k_), v in list(intersections.items()):
        if (k_, k) in intersections and intersections[k_, k] > v:
            del intersections[k_, k]

    # Generate the summary JSON
    json = [{"sets": [k], "size": n} for k, n in counts.items()]
    json.extend({"sets": list(k), "size": n} for k, n in intersections.items())

    return json
