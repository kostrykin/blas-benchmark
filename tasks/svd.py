name = 'SVD of a 2048x1024 matrix'
order = 2000


def setup(run_id):
    import numpy as np
    np.random.seed(run_id)
    return dict(
        np = np,
        A = np.random.randn(2048, 1024),
    )


def benchmark(np, A):
    return np.linalg.svd(A)
