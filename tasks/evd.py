name = 'Eigendecomposition of a 2048x2048 matrix'


def setup():
    import numpy as np
    np.random.seed(0)
    return dict(
        np = np,
        A = np.random.randn(2048, 2048),
    )


def benchmark(np, A):
    return np.linalg.eig(A)
