# Compilation parameters
COMPILE="yes"
CPUS=12

# Account specific parameter to submit compilations as a slurm job
T="00:30:00"
CLUSTER_NAME="mn5"
ACCOUNT="bsc08"

if [ $CLUSTER_NAME == "mn5" ]; then
    LOAD_PYTHON_MODULE="module load hdf5 python/3.12.1"
    MACHINE="slurm"
    QUEUE="gp_debug"
elif [ $CLUSTER_NAME == "nord4" ]; then
    LOAD_PYTHON_MODULE="module load hdf5 python/3.10.15"
    MACHINE="slurm"
else
    LOAD_PYTHON_MODULE=""
    MACHINE=""
fi
 
