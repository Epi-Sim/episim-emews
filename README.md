# episim-emew
HPC-based model exploration workflow for epidemic simulations

# Install and compile the simulator, EpiSim.jl
cd model
bash install.sh

# Install EMEWS
## Create a conda environment
conda create -n emews-env
#Install required python packages

## Activate environment
conda activate emews-env
## Install gcc compiler
conda install conda-forge::gcc
## Install swift
conda install -c swift-t swift-t

#Create experiments folder
mkdir experiments

# Run a sweep test in your computer
conda activate emews-env
bash test/test_wf_sweep.sh

# Run a sweep test in your computer
conda activate emews-env
bash test/test_wf_sweep.sh

# Run a deap test in your computer
conda activate emews-env
bash test/test_wf_deap.sh
