set -e
eval "$$(conda shell.bash hook)"

export CONDA_PREFIX="${prefix}/${config_id}/env"
export BOOTSTRAP_SH="results/${config_id}/bootstrap.sh"

echo "[${profile_id}] Conda environment: $$CONDA_PREFIX"
conda env create -f "${conda_env_filename}" --prefix "$$CONDA_PREFIX" >> "${prefix}/${config_id}.log"

conda activate "$$CONDA_PREFIX"

conda install -y -c conda-forge -c defaults pip >> "${prefix}/${config_id}.log"
pip install -r requirements.txt >> "${prefix}/${config_id}.log"

if [ -f "$$BOOTSTRAP_SH" ]
then
    source "$$BOOTSTRAP_SH" "${prefix}" "results/${config_id}"
fi

#python -m benchmark.cli ${args} --run-config "${config_id}" | sed -u "s/^/[${profile_id}] /"
python -m benchmark.cli ${args} --run-config "${config_id}"

conda deactivate
