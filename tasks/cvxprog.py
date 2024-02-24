name = 'Convex programming (logistic regression)'
order = 3000


n = 100_000


def setup(run_id):
    import numpy as np
    import cvxpy as cp
    np.random.seed(run_id)

    # Compute labels
    y = np.random.randn(1, n)
    y[y < 0] = -1
    y[y > 0] = +1

    # Compute inputs
    x = np.linspace(-1, +1, n)

    return dict(
        np = np,
        cp = cp,
        x = x,
        y = y,
    )


def benchmark(np, cp, x, y):

    # Compute features (3 rows, n columns)
    F = np.array((x ** 2, x, np.ones(n)))

    # Create model
    s = cp.Variable((1, 3))
    objective = cp.sum(cp.logistic(-cp.multiply(y, s @ F)))
    problem = cp.Problem(cp.Minimize(objective), [])

    # Solve model
    problem.solve(solver=cp.ECOS)
