set -e
eval "$$(conda shell.bash hook)"

export CONDA_PREFIX="${prefix}/${config_id}"

conda env create -f "results/${config_id}/environment.yml" --prefix "$CONDA_PREFIX"

conda activate "$CONDA_PREFIX"

python -m benchmark.cli ${args} --config "${config_id}"

rm -rf "$CONDA_PREFIX"