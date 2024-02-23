name = 'SVD of a 2048x1024 matrix'


def setup():
    import numpy as np
    np.random.seed(0)
    return dict(
        np = np,
        A = np.random.randn(2048, 1024),
    )


def benchmark(np, A):
    return np.linalg.svd(A)
