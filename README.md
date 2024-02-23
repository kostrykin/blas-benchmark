# blas-benchmark

Tasks are defined in `tasks/*.py`. The Conda environments, which specify different BLAS and with which the tasks should be run, are defined in `results/*/environment.yml`. To determine the runtime of a task, the task is repeated for at least 10 seconds, and the average is determined. The repetition and averaging procedure is repeated 3 times, and the best result is used.

**Main results:**
- [reports/AMD EPYC 7763 64-Core Processor.ipynb](https://github.com/kostrykin/blas-benchmark/blob/master/reports/AMD%20EPYC%207763%2064-Core%20Processor.ipynb)
- [reports/AMD Ryzen Threadripper 3970X 32-Core Processor.ipynb](https://github.com/kostrykin/blas-benchmark/blob/master/reports/AMD%20Ryzen%20Threadripper%203970X%2032-Core%20Processor.ipynb)

**Run the benchmark on your CPU:**
```
python -m benchmark.cli --run
```

Or only update the reports:
```
python -m benchmark.cli
```

**Acknowledgements:**
- <https://gist.github.com/cty-yyds/41bcfa6a71670527c93049aa9a5d249f>
- <https://gist.github.com/bebosudo/6f43dc6b4329c197f258f25cc69f0ec0>
- <https://danieldk.eu/Posts/2020-08-31-MKL-Zen.html>
