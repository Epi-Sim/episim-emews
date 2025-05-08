BASE_FOLDER=$(realpath .)
JULIA_VERSION=julia-1.11.4-linux-x86_64.tar.gz
JULIA_URL="https://julialang-s3.julialang.org/bin/linux/x64/1.11/${JULIA_VERSION}"

source $BASE_FOLDER/config.sh

echo " - Step 1 Installing Julia..."
if [ ! -d "julia" ]; then
  echo "- Downloading Julia..."
  wget $JULIA_URL
  tar -xvzf ${JULIA_VERSION}
  mv julia-1.11.4 julia
  rm $JULIA_VERSION
else
  echo "Julia already downloaded."
fi




export PATH=$PATH:${BASE_FOLDER}/julia/bin
export JULIA_DEPOT_PATH=${BASE_FOLDER}/.julia

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
julia install.jl

if [ $COMPILE == "yes" ]; then
  echo " - Step 3 Compiling EpiSim.jl..."
  echo "This may take a while, please be patient."
  CMD="julia install.jl -c -t ../"
  if [ $MACHINE == "slurm" ]; then
    echo "Compiling on SLURM..."
    echo "Using $CPUS CPUs"
    echo "Using $T time limit"
    echo "Using $ACCOUNT account"
    echo "Using $QUEUE queue"
    
    if [ $ACCOUNT ]; then
        A="-A $ACCOUNT"
    fi
    if [ $QUEUE ]; then
        Q="-q $QUEUE"
    fi
    CMD="julia install.jl -c -t ../"
    srun --unbuffered -t $T $A $Q -c $CPUS -n 1 $CMD |& cat
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
echo " - Step 4 Installing python requirements"
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt 
