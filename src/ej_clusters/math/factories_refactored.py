import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from sklearn.decomposition import PCA, KernelPCA
from sklearn.manifold import TSNE, Isomap, MDS, LocallyLinearEmbedding, SpectralEmbedding
from sklearn.pipeline import Pipeline
from sklearn.impute import SimpleImputer

Imputer = SimpleImputer(missing_values=np.nan, strategy='mean')

DEFAULT_ALPHA = 0.5

def random_clusterization(shape, n_comments, alpha=DEFAULT_ALPHA, missing=0.5):
    """
    Produces a full clusterization using NumPy and Pandas.
    """
    results = [random_cluster(n_users, n_comments, alpha, missing) for n_users in shape]
    votes = np.vstack([v for v, _ in results])
    centroids = np.vstack([c for _, c in results])
    return votes, centroids

def random_cluster(n_users, n_comments, alpha=DEFAULT_ALPHA, missing=0.25):
    """
    Generates a random cluster of users voting on comments.
    """
    probs = np.random.dirichlet([alpha] * 2, size=n_comments)[:, 0]
    votes = random_user_batch(n_users, probs, missing)
    
    mask = np.all(votes == 0, axis=1)
    if np.any(mask):
        votes[mask] = random_user_batch(np.sum(mask), probs, missing)

    return votes, probs

def random_user_batch(n_users, probs, missing=0.25):
    """
    Generates multiple random user profiles using vectorized operations.
    """
    rand1 = np.random.uniform(size=(n_users, len(probs)))
    rand2 = np.random.uniform(size=(n_users, len(probs)))
    users = np.ones((n_users, len(probs)), dtype=np.int8)
    users[rand1 > probs] = -1
    users[rand2 < missing] = 0
    return users

def random_probs(n_options, alpha=DEFAULT_ALPHA):
    """
    Compute random probability distributions using NumPy and Pandas.
    """
    probs = np.random.dirichlet([alpha, alpha], size=n_options)[:, 0]
    skip_probs = np.clip((1 / 3) - np.abs(probs - 0.5), 0, None)
    probs = np.stack([probs, skip_probs, 1 - probs], axis=1)
    probs /= probs.sum(axis=1, keepdims=True)
    return probs

def random_votes(sizes, n_comments, alpha=DEFAULT_ALPHA, missing=0.5):
    """
    Return a full votation based on clusters of the given sizes.
    """
    clusters = [random_cluster(size, n_comments, alpha, missing) for size in sizes]
    votes = np.vstack([v for v, _ in clusters])
    return votes

def remove_votes(votes, prob=0.5, gamma=2 * DEFAULT_ALPHA):
    """
    Randomly removes some votes using NumPy and Pandas.
    """
    votes = votes.astype(float)
    n_users, n_comments = votes.shape
    alpha = prob * 2 * gamma
    beta = (1 - prob) * 2 * gamma
    profiles = np.random.beta(alpha, beta, size=n_users)
    mask = np.random.uniform(size=(n_users, n_comments)) < profiles[:, None]
    votes[mask] = np.nan
    return votes

def sizes_to_labels(sizes, values=None):
    """
    Converts cluster sizes into corresponding labels using NumPy and Pandas.
    """
    if values is None:
        values = np.arange(len(sizes))
    return np.repeat(values, sizes)

def reduce_dimensionality(votes, method="pca", **kwargs):
    """
    Reduces the dimensionality of the votes dataset using PCA or other methods.
    
    Methods:
    * 'pca': Principal component analysis, a classic ;)
    * 't-sne': Slow, but good at keeping clustering structures
    * 'mds': Tries to preserve the distances across the original and transformed spaces
    * 'isomap': *bad?*
    * 'lle': *bad?*
    * 'se': *bad?*
    """
    standard_methods = {
        "pca": PCA,
        "k-pca": KernelPCA,
        "t-sne": TSNE,
        "isomap": Isomap,
        "mds": MDS,
        "lle": LocallyLinearEmbedding,
        "se": SpectralEmbedding,
    }
    if method not in standard_methods:
        raise ValueError(f"invalid method: {method}")

    cls = standard_methods[method]
    transformer = cls(n_components=2, **kwargs)
    pipeline = Pipeline([("imputer", Imputer), ("reducer", transformer)])
    data = pipeline.fit_transform(votes)
    return data, pipeline

def show_votes(votes, method="pca", display=True, title=None, labels=None, legend=None, **kwargs):
    """
    Show votes dataset in a 2D plot using Matplotlib and Pandas.
    """
    data, _ = reduce_dimensionality(votes, method=method, **kwargs)
    plt.figure()
    if labels is not None:
        df = pd.DataFrame(data, columns=["x", "y"])
        df["label"] = labels
        for label, group in df.groupby("label"):
            plt.scatter(group.x, group.y, label=label)
        if legend is None:
            legend = True
    else:
        plt.scatter(data[:, 0], data[:, 1])

    plt.title(title or f"Reduced votes ({method})")
    if legend:
        plt.legend()
    if display:
        plt.show()

def cluster_error(labels, true_labels):
    if len(labels) != len(true_labels):
        raise ValueError("two sets of labels must have the same size")

    e = 1e-50
    k = len(np.unique(true_labels))
    pairs = set(zip(labels, true_labels))
    return (len(pairs) - k + e) / (len(labels) - k + e)
