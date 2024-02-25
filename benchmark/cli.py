import argparse
import glob
import pathlib
import os
import sys
import json
import string
import tempfile
import csv
import itertools
import math

from .tasks import (
    tasks,
    run_task,
)
from .cpuinfo import (
    cpu_name,
)
from .profiles import (
    profiles,
)


def run_config(config_id, explicit_task_list, profiles):
    print(f'\n*** Running configuration: {config_id}\n')
    args = f'--profile "{profile["id"]}"'
    if len(explicit_task_list) > 0:
        args += '--task ' + ' '.join(f'"{task_id}"' for task_id in explicit_task_list)
    with open('templates/runscript.sh') as fp:
        template = string.Template(fp.read())
    for profile in profiles:
        with open(f'results/{config_id}/environment.yml') as fp:
            conda_env_template = string.Template(fp.read())
        with tempfile.TemporaryDirectory() as prefix:
            conda_env_filename = f'{prefix}/env.yml'
            with open(conda_env_filename, mode='w') as fp:
                fp.write(conda_env_template.substitute(**profile))
            runscript_filename = f'{prefix}/run.sh'
            with open(runscript_filename, mode='w') as fp:
                fp.write(template.substitute(config_id=config_id, profile_id=profile['id'], prefix=prefix, args=args, conda_env_filename=conda_env_filename))
            os.system(f'bash {runscript_filename}')


def create_report(profile, cpu_name, tasks, results_csv):
    import nbformat as nbf
    from nbconvert.preprocessors import ExecutePreprocessor

    nb = nbf.v4.new_notebook()
    nb['cells'] = [
        nbf.v4.new_markdown_cell(f'# {cpu_name}'),
            nbf.v4.new_code_cell(
                'import pandas as pd\n' + \
                'import numpy as np'
            ),
            nbf.v4.new_code_cell(
                f'df = pd.read_csv("{results_csv}")\n' + \
                f'df = df[df["cpu_name"] == "{cpu_name}"]\n' + \
                f'df = df[df["profile_id"] == "{profile["id"]}"]'
            ),
            nbf.v4.new_markdown_cell(
                f'**Profile:**\n' + \
                f'```json\n' + \
                f'{json.dumps(profile)}\n' + \
                f'```'
            ),
            nbf.v4.new_markdown_cell('## Highscore'),
            nbf.v4.new_markdown_cell('The *score* of a configuration is the *geometric mean* of the best possible speed-up in comparison to the other configurations.'),
            nbf.v4.new_code_cell(
                'configs = df["config_id"].unique()\n' + \
                'scores = {config_id: list() for config_id in configs}\n' + \
                'for task_id in df["task_id"].unique():\n' + \
                '    df_task = df[df["task_id"] == task_id]\n' + \
                '    for config_id in configs:\n' + \
                '        config_seconds = df_task[df_task["config_id"] == config_id]["seconds"].min()\n' + \
                '        ref_seconds = df_task["seconds"].max()\n' + \
                '        max_speedup = ref_seconds / config_seconds\n' + \
                '        scores[config_id].append(max_speedup)\n' + \
                'mean_scores = [pow(np.prod(scores[config_id]), 1 / len(scores[config_id])) for config_id in configs]\n' + \
                'df_scores = pd.DataFrame.from_dict(dict(config_id=configs, score=mean_scores))\n' + \
                'df_scores.sort_values("score", ascending=False).reset_index(drop=True)'
            ),
            nbf.v4.new_markdown_cell(f'## Benchmark details'),
    ]
    for task_idx, task_id in enumerate(sorted(tasks.keys(), key=lambda task_id: tasks[task_id].order)):
        task = tasks[task_id]
        nb['cells'] += [
            nbf.v4.new_markdown_cell(f'### Task {task_idx + 1}: {task.name}'),
            nbf.v4.new_code_cell(
                f'df_task = df[df["task_id"] == "{task_id}"]\n' + \
                f'df_task[["config_id", "seconds"]].sort_values("seconds", ascending=False)'
            ),
        ]

    ExecutePreprocessor().preprocess(nb)
    output_directory = f'reports/{profile["id"]}'
    os.makedirs(output_directory, exist_ok=True)
    with open(f'{output_directory}/{cpu_name}.ipynb', 'w') as fp:
        nbf.write(nb, fp)


if __name__ == '__main__':

    parser = argparse.ArgumentParser()
    parser.add_argument('--run-config', help=argparse.SUPPRESS)
    parser.add_argument('--run', action='store_true', help='Run the benchmarks.')
    parser.add_argument('--config', nargs='*', default=list(), help='Run only specific configuration.')
    parser.add_argument('--task', nargs='*', default=list(), help='Run only specific task.')
    parser.add_argument('--profile', nargs='+', default=list(), help='Run only for specific profiles.')
    parser.add_argument('--results-csv', default='results.csv', help='CSV with the results.')
    parser.add_argument('--clean', action='store_true', help='Remove all previous results (from all CPUs).')
    args = parser.parse_args()

    illegal_tasks = [task_id for task_id in args.task if task_id not in tasks.keys()]
    if len(illegal_tasks) > 0:
        parser.error('No such tasks: ' + ', '.join(illegal_tasks))

    illegal_profiles = [profile_id for profile_id in args.profile if profile_id not in profiles.keys()]
    if len(illegal_profiles) > 0:
        parser.error('No such profiles: ' + ', '.join(illegal_profiles))

    if args.clean:
        for json_filepath in glob.glob('results/*/*/*/*.json'):
            os.remove(json_filepath)

    if args.run_config is None:
        config_id_list = list()
        for config_path in glob.glob('results/*'):
            config_id = pathlib.Path(config_path).name
            if len(args.config) > 0 and config_id not in args.config: continue
            config_id_list.append(config_id)
            print(f'- Found config: {config_id}')
        
        print()
        if args.run:
            profiles = [profiles[profile_id] for profile_id in args.profile]
            for config_id in config_id_list:
                run_config(config_id, args.task, profiles)

        else:
            print(f'Use "--run" to run the above benchmarks (profiles: {", ".join(args.profile)}).')

        # Create summary CSV
        print(f'\nWriting results to: {args.results_csv}')
        cpu_names = set()
        with open(args.results_csv, 'w') as fp:
            csv_writer = csv.writer(fp, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)
            csv_writer.writerow(['cpu_name', 'task_id', 'config_id', 'profile_id', 'seconds'])
            for json_filepath in glob.glob('results/*/*/*/*.json'):
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
                                json_filepath.parents[2].name,
                                json_filepath.parents[1].name,
                                seconds,
                            ]
                        )
        
        # Create reports
        for cpu_name in cpu_names:
            for profile in profiles.values():
                create_report(profile, cpu_name, tasks, args.results_csv)

    else:
        for task_id, task in tasks.items():
            if len(args.task) > 0 and task_id not in args.task: continue
            for profile_id in args.profile:

                newpid = os.fork()
                if newpid != 0:

                    # Wait for the child process
                    if os.waitpid(newpid, 0)[1] != 0:
                        print('*** AN ERROR OCCURRED ***')
                        sys.exit(1)

                else:
                    
                    # Run the benchmark task
                    output_directory = f'results/{args.run_config}/{profile_id}/{task_id}'
                    os.makedirs(output_directory, exist_ok=True)
                    run_task(f'{output_directory}/{cpu_name}.json', task_id, task)

                    # Exit the child process
                    os._exit(0)
