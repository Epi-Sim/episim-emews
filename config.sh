#!/bin/bash
# Configuration parameters with defaults that can be overridden by environment variables

# Use environment variable if set, otherwise use default
# Compilation parameters
COMPILE="${COMPILE:-yes}"
CPUS="${CPUS:-3}"
T="${T:-00:20:00}"
CLUSTER_NAME="${CLUSTER_NAME:-local}"
ACCOUNT="${ACCOUNT:-bsc08}"
MEM=""
# Handle different cluster configurations
if [ "$CLUSTER_NAME" == "mn5" ]; then
    MACHINE="slurm"
    ACCOUNT="bsc08"
    QUEUE="gp_debug" # gp_bscls
    LOAD_MODULES="module load swig java-jdk/8u131 ant/1.10.14 R/4.3.2 zsh hdf5 python/3.12.1 swiftt/1.6.2-python-3.12.1"
    PPN=112
elif [ "$CLUSTER_NAME" == "nord4" ]; then
    MACHINE="slurm"
    QUEUE="${QUEUE:-}"
    QUEUE="bsc_ls"
    LOAD_MODULES="module load zsh hdf5 java/8u131 R/3.4.0 python/3.12.0 swiftt/1.5.0"
    PPN=48
elif [ "$CLUSTER_NAME" == "elastic" ]; then
    MACHINE="slurm"
    # Define memory for elastic cluster (no ACCOUNT or QUEUE needed)
    MEM="${MEM:-15G}"
    # Clear ACCOUNT and QUEUE to trigger the memory-based allocation
    ACCOUNT=""
    QUEUE=""
    # Clear LOAD_MODULES
    LOAD_MODULES=""
else
    LOAD_MODULES=""
    MACHINE="local"
    # Clear ACCOUNT and QUEUE to trigger the memory-based allocation
    ACCOUNT=""
    QUEUE=""
    # Clear LOAD_MODULES
    LOAD_MODULES=""
fi

# Echo the configuration for debugging purposes
echo "=== Configuration ==="
echo "COMPILE: $COMPILE"
echo "CPUS: $CPUS"
echo "Time limit: $T"
echo "Cluster: $CLUSTER_NAME"
echo "Machine type: $MACHINE"
[ -n "$ACCOUNT" ] && echo "Account: $ACCOUNT"
[ -n "$QUEUE" ] && echo "Queue: $QUEUE"
[ -n "$MEM" ] && echo "Memory: $MEM"
echo "===================="