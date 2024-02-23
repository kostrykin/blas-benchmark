import numpy as np


name = 'SVD of a 2048x1024 matrix'


def setup():
    np.random.seed(0)
    return dict(
        A = np.random.randn(2048, 1024),
    )


def benchmark(A):
    return np.linalg.svd(A)