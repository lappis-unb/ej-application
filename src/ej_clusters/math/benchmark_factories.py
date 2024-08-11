import timeit

# Setup code for original factories.py
setup_code_original = """
from factories import random_clusterization
shape = [100, 200, 300]
n_comments = 50
"""

# Setup code for refactored factories_refactored.py
setup_code_refactored = """
from factories_refactored import random_clusterization
shape = [100, 200, 300]
n_comments = 50
"""

# Test code for benchmarking random_clusterization function
test_code = """
random_clusterization(shape, n_comments)
"""

# Measure execution time for the original version
execution_time_original = timeit.timeit(test_code, setup=setup_code_original, number=1000)
print(f"Original execution time: {execution_time_original} seconds")

# Measure execution time for the refactored version
execution_time_refactored = timeit.timeit(test_code, setup=setup_code_refactored, number=1000)
print(f"Refactored execution time: {execution_time_refactored} seconds")
