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
    Generates a full clusterization based on specified cluster sizes and comment counts.

    Args:
        shape (list of int): A list of integers where each value represents the number of users in a cluster.
        n_comments (int): Number of comments each user votes on.
        alpha (float): Dirichlet distribution parameter that controls the randomness of voting behavior.
        missing (float): Probability that a user will not vote on a given comment.

    Returns:
        tuple: A tuple containing:
            - votes (ndarray): A 2D array where each row represents a user's voting profile.
            - centroids (ndarray): A 2D array representing the centroids of the clusters.
    """
    results = [random_cluster(n_users, n_comments, alpha, missing) for n_users in shape]
    votes = np.vstack([v for v, _ in results])
    centroids = np.vstack([c for _, c in results])
    return votes, centroids

def random_cluster(n_users, n_comments, alpha=DEFAULT_ALPHA, missing=0.25):
    """
    Generates a random cluster of users voting on comments.

    Args:
        n_users (int): Number of users in the cluster.
        n_comments (int): Number of comments each user votes on.
        alpha (float): Dirichlet distribution parameter for generating voting probabilities.
        missing (float): Probability that a user will not vote on a given comment.

    Returns:
        tuple: A tuple containing:
            - votes (ndarray): A 2D array representing the voting behavior of users in the cluster.
            - probs (ndarray): A 1D array of voting probabilities for the comments.
    """
    probs = np.random.dirichlet([alpha] * 2, size=n_comments)[:, 0]
    votes = random_user_batch(n_users, probs, missing)
    
    mask = np.all(votes == 0, axis=1)
    if np.any(mask):
        votes[mask] = random_user_batch(np.sum(mask), probs, missing)

    return votes, probs

def random_user_batch(n_users, probs, missing=0.25):
    """
    Generates voting profiles for multiple users using vectorized operations.

    Args:
        n_users (int): Number of users.
        probs (ndarray): A 1D array of probabilities for voting positively on each comment.
        missing (float): Probability that a vote will be missing.

    Returns:
        ndarray: A 2D array where each row represents a user's voting profile.
    """
    rand1 = np.random.uniform(size=(n_users, len(probs)))
    rand2 = np.random.uniform(size=(n_users, len(probs)))
    users = np.ones((n_users, len(probs)), dtype=np.int8)
    users[rand1 > probs] = -1
    users[rand2 < missing] = 0
    return users

def random_probs(n_options, alpha=DEFAULT_ALPHA):
    """
    Computes random probability distributions for a given number of options.

    Args:
        n_options (int): Number of options to generate probabilities for.
        alpha (float): Dirichlet distribution parameter for generating the probabilities.

    Returns:
        ndarray: A 2D array where each row represents the probability distribution across the options.
    """
    probs = np.random.dirichlet([alpha, alpha], size=n_options)[:, 0]
    skip_probs = np.clip((1 / 3) - np.abs(probs - 0.5), 0, None)
    probs = np.stack([probs, skip_probs, 1 - probs], axis=1)
    probs /= probs.sum(axis=1, keepdims=True)
    return probs

def random_votes(sizes, n_comments, alpha=DEFAULT_ALPHA, missing=0.5):
    """
    Generates a complete voting dataset based on cluster sizes.

    Args:
        sizes (list of int): A list where each value represents the number of users in a cluster.
        n_comments (int): Number of comments each user votes on.
        alpha (float): Dirichlet distribution parameter for generating voting probabilities.
        missing (float): Probability that a vote will be missing.

    Returns:
        ndarray: A 2D array where each row represents a user's voting profile across all clusters.
    """
    clusters = [random_cluster(size, n_comments, alpha, missing) for size in sizes]
    votes = np.vstack([v for v, _ in clusters])
    return votes

def remove_votes(votes, prob=0.5, gamma=2 * DEFAULT_ALPHA):
    """
    Randomly removes a fraction of votes from the dataset to simulate missing data.

    Args:
        votes (ndarray): A 2D array where each row represents a user's voting profile.
        prob (float): Average probability that a vote will be removed.
        gamma (float): Parameter controlling the variability of the removal process.

    Returns:
        ndarray: A 2D array with some votes removed (set to NaN).
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
    Converts cluster sizes into corresponding labels.

    Args:
        sizes (list of int): List of cluster sizes.
        values (list, optional): List of labels to assign to clusters. Defaults to None, which uses integers.

    Returns:
        ndarray: A 1D array of labels corresponding to the cluster sizes.
    """
    if values is None:
        values = np.arange(len(sizes))
    return np.repeat(values, sizes)

def reduce_dimensionality(votes, method="pca", **kwargs):
    """
    Reduces the dimensionality of the votes dataset for visualization using various methods.

    Args:
        votes (ndarray): A 2D array where each row represents a user's voting profile.
        method (str): Method for dimensionality reduction. Options include 'pca', 'k-pca', 't-sne', 'isomap', 'mds', 'lle', 'se'.
        **kwargs: Additional keyword arguments to pass to the dimensionality reduction method.

    Returns:
        tuple: A tuple containing:
            - data (ndarray): The transformed data in reduced dimensions.
            - pipeline (Pipeline): The scikit-learn pipeline used for transformation.
    
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
    Displays the votes dataset in a 2D plot after dimensionality reduction.

    Args:
        votes (ndarray): A 2D array where each row represents a user's voting profile.
        method (str): Method for dimensionality reduction. Options include 'pca', 't-sne', etc.
        display (bool): Whether to display the plot. Defaults to True.
        title (str, optional): Title of the plot. Defaults to None.
        labels (ndarray, optional): Labels for each user. Used for coloring the points. Defaults to None.
        legend (bool, optional): Whether to display the legend. Defaults to None.
        **kwargs: Additional keyword arguments for dimensionality reduction.

    Returns:
        None
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
