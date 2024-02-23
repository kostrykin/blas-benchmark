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


def run_task(output_filepath, task_id, task):
    kwargs = task.setup()
    time0 = time.time()
    task.benchmark(**kwargs)
    dt = time.time() - time0
    with open(output_filepath, 'w') as fp:
        json.dump([dt], fp)


def run_config(config_id, explicit_task_list):
    args = ' '.join(f'--task "{task_id}"' for task_id in explicit_task_list)
    with open('runscript_template.sh') as fp:
        template = string.Template(fp.read())
    with tempfile.TemporaryDirectory() as prefix:
        runscript_filename = f'{prefix}/run.sh'
        with open(runscript_filename, mode='w') as fp:
            fp.write(template.substitute(config_id=config_id, prefix=prefix, args=args))
        os.system(f'sh {runscript_filename}')


if __name__ == '__main__':

    parser = argparse.ArgumentParser()
    parser.add_argument('--config', help=argparse.SUPPRESS)
    parser.add_argument('--run', action='store_true', help='Run the benchmarks.')
    parser.add_argument('--task', nargs='*', default=list(), help='Run only specific task.')
    args = parser.parse_args()

    if args.config is None:
        config_id_list = list()
        for config_path in glob.glob('results/*'):
            config_id = pathlib.Path(config_path).name
            config_id_list.append(config_id)
            print(f'- Found config: {config_id}')
        
        print()
        if args.run:
            for config_id in config_id_list:
                run_config(config_id, args.task)

        else:
            print('Use "--run" to run the above benchmarks.')

    else:
        for task_id, task in tasks.items():
            if len(args.task) > 0 and task_id not in args.task: continue

            newpid = os.fork()
            if newpid != 0:

                # Wait for the child process.
                if os.waitpid(newpid, 0)[1] != 0:
                    sys.exit(1)

            else:
                
                # Run the benchmark task.
                output_directory = f'results/{args.config}/{task_id}'
                os.makedirs(output_directory, exist_ok=True)
                run_task(f'{output_directory}/{cpu_name}.json', task_id, task)

                # Exit the child process.
                os._exit(0)
    
    # TODO: create csv summary