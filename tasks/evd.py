import numpy as np


name = 'Eigendecomposition of a 2048x2048 matrix'


def setup():
    np.random.seed(0)
    return dict(
        A = np.random.randn(2048, 2048),
    )


def benchmark(A):
    return np.linalg.eig(A)