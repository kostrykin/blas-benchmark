name = 'Eigendecomposition of a 2048x2048 matrix'
order = 2001


def setup(run_id):
    import numpy as np
    np.random.seed(run_id)
    return dict(
        np = np,
        A = np.random.randn(2048, 2048),
    )


def benchmark(np, A):
    return np.linalg.eig(A)
