#! /usr/bin/env bash

# uncomment to turn on swift/t logging. Can also set TURBINE_LOG,
# TURBINE_DEBUG, and ADLB_DEBUG to 0 to turn off logging
# export TURBINE_LOG=1 TURBINE_DEBUG=1 ADLB_DEBUG=1
export DEBUG_MODE=2

export EMEWS_PROJECT_ROOT=$( cd $( dirname $0 )/.. ; /bin/pwd )
export PYTHONPATH=$PYTHONPATH:$EMEWS_PROJECT_ROOT/python

# source some utility functions used by EMEWS in this script
source "${EMEWS_PROJECT_ROOT}/etc/emews_utils.sh"

set -eu

if [ "$#" -ne 6 ]; then
  script_name=$(basename $0)
  echo "Usage: ${script_name} EXPERIMENT_ID (e.g. ${script_name} experiment_1) DATA_FOLDER CONFIG_JSON WOKFLOW_JSON PARAMS_SWEEP CLUSTER_NAME (mn5/nord3/local)"
  exit 1
fi

EXPID=$1
export TURBINE_OUTPUT=$EMEWS_PROJECT_ROOT/experiments/$EXPID

BASE_DATA_FOLDER=$2
DATA_FOLDER="${TURBINE_OUTPUT}/data"

BASE_CONFIG_JSON=$3
CONFIG_JSON="${TURBINE_OUTPUT}/config.json"

BASE_WORKFLOW_CONFIG=$4
WORKFLOW_CONFIG="${TURBINE_OUTPUT}/workflow_settings.json"

BASE_PARAMS_SWEEP=$5
PARAMS_SWEEP="${TURBINE_OUTPUT}/sweep_params_n10.txt"

CLUSTER_NAME=$6

#################################################################

# function that check all files exist and creates the experiment 
# folder ($TURBINE_OUTPUT) and copy all files required by the
# experiments

WORKFLOW_TYPE="SWEEP"
setup_experiment $WORKFLOW_TYPE

#################################################################
# set machine to your schedule type (e.g. pbs, slurm, cobalt etc.),
# or empty for an immediate non-queued unscheduled run
# export TURBINE_LAUNCHER=""
# MACHINE=""

if [ ${CLUSTER_NAME} = "mn5" ]; then
  # Currently julia/1.10.0 is broken in mn5 so users must have a julia isntallation in their home
  module load swig java-jdk/8u131 ant/1.10.14 R/4.3.2 zsh hdf5 python/3.12.1 swiftt/1.6.2-python-3.12.1 
  export PPN=112
  export TURBINE_LAUNCHER="srun"
  MACHINE="slurm"
  source $EMEWS_PROJECT_ROOT/venv/bin/activate
elif [ ${CLUSTER_NAME} = "nord3" ]; then
  module load python intel impi/2021.4.0 mkl/2021.4.0 java/8u131 R/4.1.0 swiftt/1.5.0 gcc julia/1.9.1
  export PPN=16
  export TURBINE_LAUNCHER="srun"
  MACHINE="slurm"
elif [ ${CLUSTER_NAME} = "pc" ]; then
  export PPN=6
  export TURBINE_LAUNCHER=""
  MACHINE=""
else
  echo "Unknown Cluster name ${CLUSTER_NAME}"
  exit 1;
fi

if [ -n "$MACHINE" ]; then
  MACHINE="-m $MACHINE"
fi

#################################################################
# Computing Resources
export PROCS=4
export PROJECT=bsc08
export WALLTIME=02:00:00
export QUEUE=gp_bscls
export TURBINE_SBATCH_ARGS="--qos=gp_bscls"
export TURBINE_JOBNAME="${EXPID}_job"

#################################################################
# log variables and script to to TURBINE_OUTPUT directory
log_script
# echo's anything following this standard out
set -x

#################################################################

SWIFT_PATH="${EMEWS_PROJECT_ROOT}/swift"
SWIFT_WF="${SWIFT_PATH}/run_wf_sweep.swift"

CMD_LINE_ARGS="-d=${DATA_FOLDER} -c=${CONFIG_JSON} -w=${WORKFLOW_CONFIG} -f=${PARAMS_SWEEP}"

swift-t -p  -n $PROCS $MACHINE -I $SWIFT_PATH  $SWIFT_WF  $CMD_LINE_ARGS


