import unittest
import numpy as np
from ej_clusters.math.kmeansjoblib import compute_distance_matrix, compute_labels
from joblib import Parallel, delayed

class TestKMeansJoblib(unittest.TestCase):
    def setUp(self):
        self.data = np.random.rand(100, 10)  
        self.centroids = np.random.rand(5, 10)  

    def test_compute_distance_matrix(self):
        distances = compute_distance_matrix(self.data, self.centroids)
        self.assertEqual(distances.shape, (100, 5))

    def test_compute_labels(self):
        labels = compute_labels(self.data, self.centroids)
        self.assertEqual(len(labels), 100)

    def test_parallel_distance_computation(self):
        def compute_distance(sample):
            return np.linalg.norm(sample - self.centroids, axis=1)

        distances = Parallel(n_jobs=-1)(delayed(compute_distance)(sample) for sample in self.data)
        self.assertEqual(len(distances), 100)

if __name__ == '__main__':
    unittest.main()
