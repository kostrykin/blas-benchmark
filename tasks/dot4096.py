name = 'Dotted two 4096x4096 matrices'
order = 1000


def setup(run_id):
    import numpy as np
    np.random.seed(run_id)
    return dict(
        A = np.random.randn(4096, 4096),
        B = np.random.randn(4096, 4096),
    )


def benchmark(A, B):
    return A @ B
