ACCOUNT="bsc08"
COMPILE="yes"
QUEUE="gp_debug"
T="00:30:00"
CPUS=12
MCHINE="slurm"
CLUSTER_NAME="mn5"

if [ $CLUSTER_NAME == "mn5" ]; then
    LOAD_PYTHON_MODULE="module load python/3.10.15"
elif [ $CLUSTER_NAME == "nord4" ]; then
    LOAD_PYTHON_MODULE="module load python/3.10.15"
else
    LOAD_PYTHON_MODULE=""
fi
 