#! /usr/bin/env bash

# uncomment to turn on swift/t logging. Can also set TURBINE_LOG,
# TURBINE_DEBUG, and ADLB_DEBUG to 0 to turn off logging
# export TURBINE_LOG=1 TURBINE_DEBUG=1 ADLB_DEBUG=1

set -eu

if [ "$#" -ne 7 ]; then
  script_name=$(basename $0)
  echo "Usage: ${script_name} EXPERIMENT_ID (e.g. ${script_name} experiment_1) DATA_FOLDER CONFIG_JSON WORKFLOW_JSON PARAMS_DEAP STRATEGY MACHINE_NAME (mn5/nord3)"
  exit 1
fi

export EMEWS_PROJECT_ROOT=$( cd $( dirname $0 )/.. ; /bin/pwd )

# source some utility functions used by EMEWS in this script
source "${EMEWS_PROJECT_ROOT}/etc/emews_utils.sh"

EXPID=$1
BASE_DATA_FOLDER=$2
BASE_CONFIG_JSON=$3
BASE_WORKFLOW_JSON=$4
BASE_PARAMS_DEAP=$5
STRATEGY=$6
CLUSTER_NAME=$7

if ([ ${STRATEGY} != "deap_ga" ] && [ ${STRATEGY} != "deap_cmaes" ]); then
    echo "Incorrect Strategy ${STRATEGY}. Posible optiones a deap_ga and deap_cmaes"
    exit 1;
fi

export TURBINE_OUTPUT=$EMEWS_PROJECT_ROOT/experiments/$EXPID

check_directory_exists
mkdir -p ${TURBINE_OUTPUT}

DATA_FOLDER="${TURBINE_OUTPUT}/data"
CONFIG_JSON="${TURBINE_OUTPUT}/config.json"
WORKFLOW_JSON="${TURBINE_OUTPUT}/workflow_settings.json"
PARAMS_DEAP="${TURBINE_OUTPUT}/deap_params.json"

####################################i##########
# Copying data folder into turbine output
##############################################
if [ ! -d "${BASE_DATA_FOLDER}" ]; then
    echo "Base data folder ${BASE_DATA_FOLDER} doe not exists"
    exit 1;
fi

if [ ! -d "${DATA_FOLDER}" ]; then
    echo "Creating data folder at turbine output"
    mkdir ${DATA_FOLDER}
fi

echo "Copying data files into turbine output"
cp ${BASE_DATA_FOLDER}/* ${DATA_FOLDER}

##################################################
# Copying base config file into turbine output
##################################################
if [ -f "${BASE_CONFIG_JSON}" ]; then
  echo "Copying base config file into turbine output"
  cp ${BASE_CONFIG_JSON} ${CONFIG_JSON}
else
  echo "Base config file ${BASE_CONFIG_JSON} doe not exists"
  exit 1;
fi

########################################################
# Copying base workflow config file into turbine output
########################################################
if [ -f "${BASE_WORKFLOW_JSON}" ]; then
  echo "Copying base config file into turbine output"
  cp ${BASE_WORKFLOW_JSON} ${WORKFLOW_JSON}
else
  echo "Base config file ${BASE_WORKFLOW_JSON} doe not exists"
  exit 1;
fi

##################################################
# Copying base config file into turbine output
##################################################
if [ -f "${BASE_PARAMS_DEAP}" ]; then
  echo "Copying base config file into turbine output"
  cp ${BASE_PARAMS_DEAP} ${PARAMS_DEAP}
else
  echo "Base param sweep file ${BASE_PARAMS_DEAP} doe not exists"
  exit 1;
fi


# Computing Resources

export PROCS=336
export PROJECT=bsc08
export WALLTIME=02:00:00
export QUEUE=gp_bscls
export TURBINE_SBATCH_ARGS="--qos=gp_bscls"
export TURBINE_JOBNAME="${EXPID}_job"

export DEBUG_MODE=2


if [ ${CLUSTER_NAME} = "mn5" ]; then
  module load swig java-jdk/8u131 ant/1.10.14 R/4.3.2 zsh hdf5 python/3.12.1 swiftt/1.6.2-python-3.12.1 julia/1.10.0
  source $EMEWS_PROJECT_ROOT/venv/bin/activate
  export PPN=112
elif [ ${CLUSTER_NAME} = "local" ]; then
  export PPN=8
else
  echo "Unknown Cluster name ${CLUSTER_NAME}"
  exit 1;
fi

export PYTHONPATH="${PYTHONPATH}:${EMEWS_PROJECT_ROOT}/python"
export PYTHONPATH="${PYTHONPATH}:${EMEWS_PROJECT_ROOT}/ext/EQ-Py"


# set machine to your schedule type (e.g. pbs, slurm, cobalt etc.),
# or empty for an immediate non-queued unscheduled run
export TURBINE_LAUNCHER="srun"
MACHINE="slurm"

if [ -n "$MACHINE" ]; then
  MACHINE="-m $MACHINE"
fi


# log variables and script to to TURBINE_OUTPUT directory
log_script
# echo's anything following this standard out
set -x

# Resident task workers and ranks
export TURBINE_RESIDENT_WORK_WORKERS=1
export RESIDENT_WORK_RANKS=$(( PROCS - 2 ))

# Parameters for the GA/CMA
ITERATIONS=10
NUM_POPULATION=5
SEED=1234
SIGMA=1
NUM_OBJECTIVES=3

SWIFT_PATH="${EMEWS_PROJECT_ROOT}/swift"
SWIFT_WF="${SWIFT_PATH}/run_wf_deap.swift"

# EQ/Py location
EQPY="$EMEWS_PROJECT_ROOT/ext/EQ-Py"

CMD_LINE_ARGS="-d=${DATA_FOLDER} -c=${CONFIG_JSON}
               -w=${WORKFLOW_JSON}
               -me_algo=${STRATEGY}  -ea_params=${PARAMS_DEAP}
               -np=${NUM_POPULATION}  -ni=${ITERATIONS}  
               -seed=${SEED}  -sigma=${SIGMA} -nobjs=${NUM_OBJECTIVES}"

swift-t -p  -n $PROCS $MACHINE -I $EQPY -r $EQPY -I $SWIFT_PATH  $SWIFT_WF  $CMD_LINE_ARGS


