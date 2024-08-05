import time
import numpy as np
from numpy.testing import assert_almost_equal, assert_equal
from ej_clusters.math.kmeans import kmeans as kmeans_original
from ej_clusters.math.kmeansjoblib import kmeans as kmeans_parallel

# Create a large dataset for benchmarking
data = np.random.rand(2000, 100)  # 20000 samples, 50 features
k = 10  # Number of clusters
n_runs = 5  # Number of runs

# Benchmark original implementation
start_time = time.time()
labels_original, centroids_original = kmeans_original(data, k, n_runs=n_runs)
original_duration = time.time() - start_time
print(f"Original kmeans duration: {original_duration:.2f} seconds")

# Benchmark parallel implementation
start_time = time.time()
labels_parallel, centroids_parallel = kmeans_parallel(data, k, n_runs=n_runs)
parallel_duration = time.time() - start_time
print(f"Parallel kmeans duration: {parallel_duration:.2f} seconds")

# Compare results for accuracy
try:
    assert_equal(labels_original, labels_parallel)
    assert_almost_equal(centroids_original, centroids_parallel, decimal=5)
    print("Accuracy check: PASSED")
except AssertionError:
    print("Accuracy check: FAILED")


# Compare results
print(f"Performance improvement: {original_duration / parallel_duration:.2f}x faster")

#I made some tests and the bigger the sample, the more the performance improves