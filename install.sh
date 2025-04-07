JULIA_URL="https://julialang-s3.julialang.org/bin/linux/x64/1.11/julia-1.11.4-linux-x86_64.tar.gz"
ACCOUNT="bsc08"
COMPILE="no"
QUEUE="gp_bscls"
T="00:30:00"
CPUS=12
MACHINE=""

echo "Installing EpiSim.jl..."
echo "Downloading Julia..."
if [ ! -d "julia" ]; then
  echo "Downloading Julia..."
  wget $JULIA_URL
else
  echo "Julia already downloaded."
fi
if [ $? -ne 0 ]; then
  echo "Failed to download Julia."
  exit 1
fi

tar -xvzf julia-1.11.4-linux-x86_64.tar.gz
mv julia-1.11.4 julia
if [ -d "julia" ]; then
  echo "Julia extracted successfully."
else
  echo "Failed to extract Julia."
  exit 1
fi
export PATH=$PATH:$(pwd)/julia/bin
if [ -d "julia" ]; then
  echo "Julia is already installed."
else
  echo "Julia installation failed."
  exit 1
fi

if [ ! -d "model" ]; then
  mkdir model
fi
cd model
git clone https://github.com/Epi-Sim/EpiSim.jl.git
cd EpiSim.jl/

if [ $COMPILE == "yes" ]; then
  echo "Compiling EpiSim.jl..."
  echo "This may take a while, please be patient."
  if [ $MACHINE == "slurm" ]; then
    echo "Compiling on SLURM..."
    echo "Using $CPUS CPUs"
    echo "Using $T time limit"
    echo "Using $ACCOUNT account"
    echo "Using $QUEUE queue"
    CMD="julia install.jl -c -t ../"
    if [ $ACCOUNT ]; then
        A="-A $ACCOUNT"
    fi
    if [ $QUEUE ]; then
        Q="--qos=$QUEUE"
    fi
    srun --unbuffered -t $T $A $Q -c $CPUS -n 1 $CMD |& cat
  else
    echo "Compiling on local machine..."
    echo "Using $CPUS CPUs"
    julia install.jl -c -i -t ../
  fi
  cd ..
else
  julia install.jl
  EPISIM_PATH=$(realpath .)/src/run.jl
  cd .. 
  echo "#!/bin/bash" > ./episim
  echo "julia \"$EPISIM_PATH\" \"$@\"" >> ./episim
  chmod +x ./episim
fi

echo "EpiSim.jl installed successfully."
echo "To run the simulation, use the command: ./model/episim <arguments>"


 python3 -m venv venv
 source venv/bin/activate
 pip install -r requirements.txt 
