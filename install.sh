#!/bin/bash
# Usage: ./install.sh [CLUSTER_NAME]
# Example: ./install.sh elastic


# Set cluster name from command line argument or use default
export CLUSTER_NAME="${1:-mn5}"
echo "Using cluster: $CLUSTER_NAME"

BASE_FOLDER=$(realpath "$(dirname "${BASH_SOURCE[0]}")")

################################################################## 

JULIA_VERSION=julia-1.11.4-linux-x86_64.tar.gz
JULIA_URL="https://julialang-s3.julialang.org/bin/linux/x64/1.11/${JULIA_VERSION}"

export PATH=$PATH:${BASE_FOLDER}/julia/bin
export JULIA_DEPOT_PATH=${BASE_FOLDER}/.julia

# Source config.sh - all other parameters will be determined based on CLUSTER_NAME
source $BASE_FOLDER/config.sh

echo " - Step 1 Installing Julia..."
if [ ! -d "julia" ]; then
  echo "- Downloading Julia..."
  wget $JULIA_URL
  echo "- Extracting Julia..."
  tar -xzf ${JULIA_VERSION}
  mv julia-1.11.4 julia
  rm $JULIA_VERSION
else
  echo "- Julia already downloaded."
fi

################################################################## 

echo " - Step 2 Installing EpiSim.jl..."

if [ ! -d "model" ]; then
  mkdir model
fi
cd model
if [ -d "EpiSim.jl" ]; then
  rm -fr EpiSim.jl
fi


git clone https://github.com/Epi-Sim/EpiSim.jl.git
cd EpiSim.jl/
echo " - Installing EpiSim.jl dependencies"
julia install.jl

if [ $COMPILE == "yes" ]; then
  echo " - Step 3 Compiling EpiSim.jl..."
  echo "This may take a while, please be patient."
  CMD="julia install.jl -c -t ../"
  
  if [ $MACHINE == "slurm" ]; then
    echo "Compiling on SLURM..."
    echo "Using $CPUS CPUs"
    echo "Using $T time limit"
    
    if [ -n "$ACCOUNT" ] && [ -n "$QUEUE" ]; then
      echo "Using $ACCOUNT account"
      echo "Using $QUEUE queue"
      A="-A $ACCOUNT"
      Q="-q $QUEUE"
      srun --unbuffered -t $T $A $Q -c $CPUS -n 1 $CMD |& cat
    else
      echo "No account and queue defined, using memory allocation instead"
      echo "Using $MEM memory"
      srun --unbuffered -t $T --mem=$MEM -c $CPUS -n 1 $CMD |& cat
    fi
  else
    echo "Compiling on local machine..."
    echo "Using $CPUS CPUs"
    julia install.jl -c -i -t ../
  fi
  cd ..
else
  cd .. 
  EPISIM_PATH="${BASE_FOLDER}/model/EpiSim.jl/src/run.jl"
  echo "julia \"$EPISIM_PATH\"" \$@ > ./episim
  chmod +x ./episim
fi

echo "EpiSim.jl installed successfully."
echo "To run the simulation, use the command: ./model/episim <arguments>"
cd $BASE_FOLDER

################################################################## 

echo " - Step 4 Installing python requirements"

# Load python module if specified
if [ -n "$LOAD_MODULES" ]; then
  echo "Loading required module: $LOAD_MODULES"
  eval $LOAD_MODULES
fi

python -m venv $BASE_FOLDER/venv
source $BASE_FOLDER/venv/bin/activate
pip install -r $BASE_FOLDER/requirements.txt

echo "Python dependecies installed successfully."