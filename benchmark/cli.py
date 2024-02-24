import argparse
import glob
import importlib
import pathlib
import subprocess
import re
import os
import sys
import time
import json
import string
import tempfile
import csv
import itertools
import math


tasks = dict()
for task_filepath in glob.glob('tasks/*.py'):
    if task_filepath == 'tasks/__init__.py': continue
    task_filepath = pathlib.Path(task_filepath)
    task_id = task_filepath.stem
    task = importlib.import_module(f'tasks.{task_id}')
    tasks[task_id] = task


cpu_info = frozenset(subprocess.check_output('cat /proc/cpuinfo |grep -i "model name"', shell=True).decode().strip().split('\n'))
if len(cpu_info) == 1:
    cpu_info = next(iter(cpu_info))
    cpu_name = re.match(r'^.+: +(.+)$', cpu_info).group(1)
else:
    cpu_name = None


def timeit(func, *args, **kwargs):
    time0 = time.time()
    task.benchmark(*args, **kwargs)
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


def run_config(config_id, explicit_task_list):
    print(f'\n*** Running configuration: {config_id}\n')
    args = ' '.join(f'--task "{task_id}"' for task_id in explicit_task_list)
    with open('templates/runscript.sh') as fp:
        template = string.Template(fp.read())
    with tempfile.TemporaryDirectory() as prefix:
        runscript_filename = f'{prefix}/run.sh'
        with open(runscript_filename, mode='w') as fp:
            fp.write(template.substitute(config_id=config_id, prefix=prefix, args=args))
        os.system(f'bash {runscript_filename}')


def create_report(cpu_name, tasks, results_csv):
    import nbformat as nbf
    from nbconvert.preprocessors import ExecutePreprocessor

    nb = nbf.v4.new_notebook()
    nb['cells'] = [
        nbf.v4.new_markdown_cell(f'# {cpu_name}'),
            nbf.v4.new_code_cell(f'import pandas as pd'),
            nbf.v4.new_code_cell(
                f'df = pd.read_csv("{results_csv}")\n' + \
                f'df = df[df["cpu_name"] == "{cpu_name}"]'
            ),
    ]
    for task_id in sorted(tasks.keys(), key=lambda task_id: tasks[task_id].order):
        task = tasks[task_id]
        nb['cells'] += [
            nbf.v4.new_markdown_cell(f'### {task.name}'),
            nbf.v4.new_code_cell(
                f'df_task = df[df["task_id"] == "{task_id}"]\n' + \
                f'df_task[["config_id", "seconds"]].sort_values("seconds", ascending=False)'
            ),
        ]

    ExecutePreprocessor().preprocess(nb)
    os.makedirs('reports', exist_ok=True)
    with open(f'reports/{cpu_name}.ipynb', 'w') as fp:
        nbf.write(nb, fp)


if __name__ == '__main__':

    parser = argparse.ArgumentParser()
    parser.add_argument('--run-config', help=argparse.SUPPRESS)
    parser.add_argument('--run', action='store_true', help='Run the benchmarks.')
    parser.add_argument('--config', nargs='*', default=list(), help='Run only specific configuration.')
    parser.add_argument('--task', nargs='*', default=list(), help='Run only specific task.')
    parser.add_argument('--results-csv', default='results.csv', help='CSV with the results.')
    args = parser.parse_args()

    illegal_tasks = [task_id for task_id in args.task if task_id not in tasks.keys()]
    if len(illegal_tasks) > 0:
        parser.error('No such tasks: ' + ', '.join(illegal_tasks))
        sys.exit(1)

    if args.run_config is None:
        config_id_list = list()
        for config_path in glob.glob('results/*'):
            config_id = pathlib.Path(config_path).name
            if len(args.config) > 0 and config_id not in args.config: continue
            config_id_list.append(config_id)
            print(f'- Found config: {config_id}')
        
        print()
        if args.run:
            for config_id in config_id_list:
                run_config(config_id, args.task)

        else:
            print('Use "--run" to run the above benchmarks.')

        # Create summary CSV
        print(f'\nWriting results to: {args.results_csv}')
        cpu_names = set()
        with open(args.results_csv, 'w') as fp:
            csv_writer = csv.writer(fp, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)
            csv_writer.writerow(['cpu_name', 'task_id', 'config_id', 'seconds'])
            for json_filepath in glob.glob('results/*/*/*.json'):
                json_filepath = pathlib.Path(json_filepath)
                with open(json_filepath, 'r') as fp_json:
                    data = json.load(fp_json)
                    for seconds in data:
                        cpu_name = json_filepath.stem
                        cpu_names.add(cpu_name)
                        csv_writer.writerow(
                            [
                                cpu_name,
                                json_filepath.parents[0].name,
                                json_filepath.parents[1].name,
                                seconds,
                            ]
                        )
        
        # Create reports
        for cpu_name in cpu_names:
            create_report(cpu_name, tasks, args.results_csv)

    else:
        for task_id, task in tasks.items():
            if len(args.task) > 0 and task_id not in args.task: continue

            newpid = os.fork()
            if newpid != 0:

                # Wait for the child process
                if os.waitpid(newpid, 0)[1] != 0:
                    print('*** AN ERROR OCCURRED ***')
                    sys.exit(1)

            else:
                
                # Run the benchmark task
                output_directory = f'results/{args.run_config}/{task_id}'
                os.makedirs(output_directory, exist_ok=True)
                run_task(f'{output_directory}/{cpu_name}.json', task_id, task)

                # Exit the child process
                os._exit(0)
