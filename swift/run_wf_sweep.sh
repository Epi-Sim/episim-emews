#! /usr/bin/env bash

# uncomment to turn on swift/t logging. Can also set TURBINE_LOG,
# TURBINE_DEBUG, and ADLB_DEBUG to 0 to turn off logging
# export TURBINE_LOG=1 TURBINE_DEBUG=1 ADLB_DEBUG=1
export DEBUG_MODE=2

export EMEWS_PROJECT_ROOT=$( cd $( dirname $0 )/.. ; /bin/pwd )
export PYTHONPATH=${PYTHONPATH:-}:$EMEWS_PROJECT_ROOT/python

# source some utility functions used by EMEWS in this script
source "${EMEWS_PROJECT_ROOT}/etc/emews_utils.sh"
source "${EMEWS_PROJECT_ROOT}/etc/cluster_settings.sh"

# -e: exit immediately on any error
# -u: treat unset variables as an error and exit
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
PARAMS_SWEEP="${TURBINE_OUTPUT}/sweep_params.txt"

CLUSTER_NAME=$6

load_cluster_setting $CLUSTER_NAME
echo "Load required modules and exporting CLUSTER settings"

#################################################################

# function that check all files exist and creates the experiment 
# folder ($TURBINE_OUTPUT) and copy all files required by the
# experiments

WORKFLOW_TYPE="SWEEP"
setup_test_experiment $WORKFLOW_TYPE


#################################################################
# Computing Resources
export PROCS=336
export PROJECT=bsc08
export WALLTIME=02:00:00

# set machine to your schedule type (e.g. pbs, slurm, cobalt etc.),
# or empty for an immediate non-queued unscheduled run

if [ "$MACHINE" == "slurm" ]; then
  export TURBINE_LAUNCHER="srun"
  export TURBINE_SBATCH_ARGS="--qos=${QUEUE}"
fi

if [ -n "$MACHINE" ]; then
  MACHINE="-m $MACHINE"
fi

#################################################################
# log variables and script to to TURBINE_OUTPUT directory
log_script
# echo's anything following this standard out
set -x

#################################################################

SWIFT_PATH="${EMEWS_PROJECT_ROOT}/swift"
SWIFT_WF="${SWIFT_PATH}/run_wf_sweep.swift"

CMD_LINE_ARGS="-d=${DATA_FOLDER} -c=${CONFIG_JSON} -w=${WORKFLOW_CONFIG} -f=${PARAMS_SWEEP}"


swift-t -p -n $PROCS $MACHINE -I $SWIFT_PATH $SWIFT_WF $CMD_LINE_ARGS

