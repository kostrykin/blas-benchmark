set -e
eval "$$(conda shell.bash hook)"

export CONDA_PREFIX="${prefix}/${config_id}/env"
export BOOTSTRAP_SH="results/${config_id}/bootstrap.sh"

echo "Conda environment: $$CONDA_PREFIX"
conda env create -f "results/${config_id}/environment.yml" --prefix "$$CONDA_PREFIX" > "${prefix}/${config_id}.log"

conda activate "$$CONDA_PREFIX"

if [ -f "$$BOOTSTRAP_SH" ]
then
    source "$$BOOTSTRAP_SH" "${prefix}" "results/${config_id}"
fi

python -m benchmark.cli ${args} --run-config "${config_id}"

conda deactivate
