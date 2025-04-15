


load_cluster_setting() {

    CLUSTER_NAME=$1

    if [ $CLUSTER_NAME == "mn5" ]; then
        module load swig java-jdk/8u131 ant/1.10.14 R/4.3.2 zsh hdf5 python/3.12.1 swiftt/1.6.2-python-3.12.1
        ACCOUNT="bsc08"
        MACHINE="slurm"
        QUEUE="gp_bscls"
        PPN=112

    elif [ $CLUSTER_NAME == "nord4" ]; then
        LOAD_PYTHON_MODULE=""
        MACHINE="slurm"
        QUEUE="gp_bscls"
        PPN=48
    else
        LOAD_PYTHON_MODULE=""
        MACHINE="local"
        QUEUE=""
        PPN=12
    fi

    export $MODULE_LOAD
    export $ACCOUNT
    export $MACHINE
    export $QUEUE
    export $PPN
}