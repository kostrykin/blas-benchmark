# blas-benchmark

Tasks are defined in `tasks/*.py`. The Conda environments, which specify different BLAS and with which the tasks should be run, are defined in `results/*/environment.yml`. To determine the runtime of a task, the task is repeated for at least 10 seconds, and the average is determined. The repetition and averaging procedure is repeated 3 times, and the best result is used.

## Main results:

The configurations <code>mkl2020.0_debug</code> and <code>mkl2020.1_fakeintel</code> perform overall best:

<table>
  <tr>
    <th rowspan="2">&nbsp;</th>
    <th colspan="2">AMD Ryzen Threadripper 3970X</th>
    <th>AMD EPYC 7763</th>
  <tr>
    <td><a href="https://github.com/kostrykin/blas-benchmark/blob/dev-profiles/reports/py38_2threads/AMD%20Ryzen%20Threadripper%203970X%2032-Core%20Processor.ipynb">2 threads</a></td>
    <td><a href="https://github.com/kostrykin/blas-benchmark/blob/dev-profiles/reports/py38_16threads/AMD%20Ryzen%20Threadripper%203970X%2032-Core%20Processor.ipynb">16 threads</a></td>
    <td><a href="https://github.com/kostrykin/blas-benchmark/blob/dev-profiles/reports/py38_2threads/AMD%20EPYC%207763%2064-Core%20Processor.ipynb">2 threads</a></td>
  </tr>
  <tr>
    <td><code>openblas</code></td>
    <td>1.003829</td>
    <td>1.019895</td>
    <td>1.016262</td>
  </tr>
  <tr>
    <td><code>mkl2024.0</code></td>
    <td>1.128423</td>
    <td>1.213864</td>
    <td>1.065984</td>
  </tr>
  <tr>
    <td><code>mkl2020.0_debug</code></td>
    <td><b>1.156737</b></td>
    <td>1.261223</td>
    <td>1.162273</td>
  </tr>
  <tr>
    <td><code>mkl2020.1_fakeintel</code></td>
    <td>1.144065</td>
    <td><b>1.281782</b></td>
    <td><b>1.164156</b></td>
  </tr>
</table>

The *score* of a configuration is the *geometric mean* of the best possible speed-up in comparison to the other configurations. See `reports/*.ipynb` for details.

## Benchmark CLI:

Run the benchmark on your CPU:
```
python -m benchmark.cli --profiles py38_2threads py38_16threads --run
```

Or only update the reports:
```
python -m benchmark.cli
```

## Acknowledgements:
- <https://gist.github.com/cty-yyds/41bcfa6a71670527c93049aa9a5d249f>
- <https://gist.github.com/bebosudo/6f43dc6b4329c197f258f25cc69f0ec0>
- <https://danieldk.eu/Posts/2020-08-31-MKL-Zen.html>
