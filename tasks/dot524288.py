import numpy as np


name = 'Dotted two vectors of length 524288'


def setup():
    np.random.seed(0)
    return dict(
        a = np.random.randn(524288),
        b = np.random.randn(524288),
    )


def benchmark(a, b):
    return a @ b