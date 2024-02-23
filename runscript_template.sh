set -e
eval "$(conda shell.bash hook)"

conda env create -f results/${ config_id }/environment.yml --prefix ${ prefix }

conda activate ${ prefix }/${ config_id }

python -m benchmark.cli --config "${ config_id }"

rm -rf ${ prefix }/${ config_id }