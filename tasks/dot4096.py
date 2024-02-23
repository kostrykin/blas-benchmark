import numpy as np


name = 'Dotted two 4096x4096 matrices'


def setup():
    np.random.seed(0)
    return dict(
        A = np.random.randn(4096, 4096),
        B = np.random.randn(4096, 4096),
    )


def benchmark(A, B):
    return A @ B