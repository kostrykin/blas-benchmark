# blas-benchmark

Tasks are defined in `tasks/*.py`. Conda environments with which the tasks should be run are defined in `results/*/environment.yml`. To determine the runtime of a task, the task is repeated for at least 10 seconds, and the average is determined. The repetition and averaging procedure is repeated 3 times, and the best result is used.

**Run the benchmark:**
```
python -m benchmark.cli --run
```

Or only update the reports:
```
python -m benchmark.cli
```

**See also:**
- <https://gist.github.com/cty-yyds/41bcfa6a71670527c93049aa9a5d249f>
- <https://danieldk.eu/Posts/2020-08-31-MKL-Zen.html>
