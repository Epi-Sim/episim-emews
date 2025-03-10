EXPID="test_sweep"

export EMEWS_PROJECT_ROOT=$( cd $( dirname $0 )/.. ; /bin/pwd )
export TURBINE_OUTPUT=$EMEWS_PROJECT_ROOT/experiments/$EXPID
export PYTHONPATH="${PYTHONPATH}:${EMEWS_PROJECT_ROOT}/python"
export DEBUG_MODE=2

source "${EMEWS_PROJECT_ROOT}/etc/emews_utils.sh"

#################################################################

BASE_DATA_FOLDER="${EMEWS_PROJECT_ROOT}/data/mitma"
DATA_FOLDER="${TURBINE_OUTPUT}/data"

BASE_CONFIG_JSON="${BASE_DATA_FOLDER}/config_MMCACovid19.json"
CONFIG_JSON="${TURBINE_OUTPUT}/config.json"

BASE_WORKFLOW_CONFIG="${BASE_DATA_FOLDER}/workflow_settings.json"
WORKFLOW_CONFIG="${TURBINE_OUTPUT}/workflow_settings.json"

BASE_PARAMS_SWEEP="${BASE_DATA_FOLDER}/sweep_params_n10.txt"
PARAMS_SWEEP="${TURBINE_OUTPUT}/sweep_params_n10.txt"

#################################################################
# source some utility functions used by EMEWS in this script


WORKFLOW_TYPE="SWEEP"
setup_test_experiment $WORKFLOW_TYPE

#################################################################

PROCS=3
SWIFT_PATH="${EMEWS_PROJECT_ROOT}/swift"
SWIFT_EXE="${SWIFT_PATH}/run_wf_sweep.swift"

CMD_LINE_ARGS="-d=${DATA_FOLDER} -c=${CONFIG_JSON} -w=${WORKFLOW_CONFIG} -f=${PARAMS_SWEEP}"

swift-t -p  -n $PROCS  -I $SWIFT_PATH  $SWIFT_EXE  $CMD_LINE_ARGS