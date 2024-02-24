name = 'Dotted two vectors of length 524288'
order = 1001


def setup(run_id):
    import numpy as np
    np.random.seed(run_id)
    return dict(
        a = np.random.randn(524288),
        b = np.random.randn(524288),
    )


def benchmark(a, b):
    return a @ b
