STRATEGY="deap_cmaes"
EXPID="test_${STRATEGY}"

export EMEWS_PROJECT_ROOT=$( cd $( dirname $0 )/.. ; /bin/pwd )
export TURBINE_OUTPUT=$EMEWS_PROJECT_ROOT/experiments/$EXPID
export PYTHONPATH="${PYTHONPATH}:"${EMEWS_PROJECT_ROOT}/python""
export PYTHONPATH="${PYTHONPATH}:"${EMEWS_PROJECT_ROOT}/ext/EQ-Py""
export EQPY="$EMEWS_PROJECT_ROOT/ext/EQ-Py"
export DEBUG_MODE=2

# source some utility functions used by EMEWS in this script
source "${EMEWS_PROJECT_ROOT}/etc/emews_utils.sh"

#################################################################

BASE_DATA_FOLDER="${EMEWS_PROJECT_ROOT}/data/mitma"
DATA_FOLDER="${TURBINE_OUTPUT}/data"

BASE_CONFIG_JSON="${BASE_DATA_FOLDER}/config.json"
CONFIG_JSON="${TURBINE_OUTPUT}/config.json"

BASE_WORKFLOW_CONFIG="${BASE_DATA_FOLDER}/workflow_settings.json"
WORKFLOW_CONFIG="${TURBINE_OUTPUT}/workflow_settings.json"

BASE_PARAMS_DEAP="${BASE_DATA_FOLDER}/deap_epiparams.json"
PARAMS_DEAP="${TURBINE_OUTPUT}/deap_epiparams.json"

#################################################################

WORKFLOW_TYPE="DEAP"
setup_test_experiment $WORKFLOW_TYPE

if [ ! -f "${BASE_PARAMS_DEAP}" ]; then
    echo "Sweep file ${BASE_PARAMS_DEAP} does not exist"
    exit;
fi

echo "Copying base deap params file into turbine output"
cp ${BASE_PARAMS_DEAP} ${PARAMS_DEAP}

# Resident task workers and ranks
export PROCS=5
export TURBINE_RESIDENT_WORK_WORKERS=1
export RESIDENT_WORK_RANKS=$(( PROCS - 2 ))

# Parameters for DEAP algorithm
GENERATIONS=5
POPULATION=5
SEED=1234
SIGMA=1

SWIFT_PATH="${EMEWS_PROJECT_ROOT}/swift"
SWIFT_EXE="${SWIFT_PATH}/run_wf_deap.swift"

# Setting the command line
CMD_LINE_ARGS="-d=${DATA_FOLDER} -c=${CONFIG_JSON} -w=${WORKFLOW_CONFIG}
                -me_algo=${STRATEGY}  -ea_params=${PARAMS_DEAP}
                -np=${POPULATION}  -ni=${GENERATIONS}  -seed=${SEED}  -sigma=${SIGMA}"


swift-t -p -n $PROCS -I $EQPY -r $EQPY -I $SWIFT_PATH  $SWIFT_EXE  $CMD_LINE_ARGS
