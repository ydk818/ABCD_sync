#!/bin/sh

#SBATCH --job-name=process_timeseries_dest
#SBATCH --output=Job_Logs/%x_%j.out
#SBATCH --error=Job_Logs/%x_%j.err

#SBATCH --partition=short
#SBATCH --time=3:00:00
#SBATCH --mem=16G

#SBATCH --nodes=1
#SBATCH --ntasks-per-node=1 
#SBATCH --cpus-per-task=1

#SBATCH --array=1-300

cd ${SLURM_SUBMIT_DIR}

# gordon_abox
# glasser_abox
# difumo_256_volume
# difumo_64_volume
# destrieux_abox

python process_timeseries.py destrieux_abox