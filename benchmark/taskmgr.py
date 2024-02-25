import glob
import time
import pathlib
import importlib
import math
import itertools
import json


tasks = dict()
for task_filepath in glob.glob('tasks/*.py'):
    if task_filepath == 'tasks/__init__.py': continue
    task_filepath = pathlib.Path(task_filepath)
    task_id = task_filepath.stem
    task = importlib.import_module(f'tasks.{task_id}')
    tasks[task_id] = task


def timeit(func, *args, **kwargs):
    time0 = time.time()
    func(*args, **kwargs)
    return time.time() - time0


def run_task(output_filepath, task_id, task, best_of=3, min_measure_time=10, max_n=100):

    # Run pre-analysis to determine the *rough* runtime
    kwargs = task.setup(0)
    dt0 = timeit(task.benchmark, **kwargs)

    # Compute the likely required number of parameters
    m = math.ceil(min_measure_time / dt0)
    n = min((m, max_n))
    print(f'{task_id}: Pre-computing n={n} benchmark parameters for about {m} repetition(s)')
    kwargs_list = [task.setup(i + 1) for i in range(n)]

    # Perform analysis multiple times...
    times = list()
    for _ in range(best_of):

        # ...and each time for at least `min_measure_time` seconds
        time0 = time.time()
        for run_idx in itertools.count(0):
            kwargs = kwargs_list[run_idx % len(kwargs_list)]
            task.benchmark(**kwargs)
            dt = time.time() - time0
            if dt >= min_measure_time:
                break
        times.append(dt / (run_idx + 1))

    # Keep the best time
    with open(output_filepath, 'w') as fp:
        json.dump([min(times)], fp)
