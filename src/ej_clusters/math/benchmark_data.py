import timeit

# Setup code for original data.py
setup_code_original = """
from data import compute_cluster_affinities
import numpy as np
import pandas as pd

# Generate fake votes data
votes = pd.DataFrame(np.random.rand(100, 50))
votes['cluster'] = np.random.randint(0, 5, size=100)
"""

# Setup code for refactored data_refactored.py
setup_code_refactored = """
from data_refactored import compute_cluster_affinities
import numpy as np
import pandas as pd

# Generate fake votes data
votes = pd.DataFrame(np.random.rand(100, 50))
votes['cluster'] = np.random.randint(0, 5, size=100)
"""

# Test code for benchmarking compute_cluster_affinities function
test_code = """
compute_cluster_affinities(votes)
"""

# Measure execution time for the original version
execution_time_original = timeit.timeit(test_code, setup=setup_code_original, number=1000)
print(f"Original execution time: {execution_time_original} seconds")

# Measure execution time for the refactored version
execution_time_refactored = timeit.timeit(test_code, setup=setup_code_refactored, number=1000)
print(f"Refactored execution time: {execution_time_refactored} seconds")
