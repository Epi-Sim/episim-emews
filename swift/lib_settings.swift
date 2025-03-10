import io;
import sys;

//####################################
// ACCESSING ENVIRONEMENTLA VARIABLES
//####################################

// Base path for the experiment
string emews_root     = getenv("EMEWS_PROJECT_ROOT");
string turbine_output = getenv("TURBINE_OUTPUT");
int    debug_mode     = string2int(getenv("DEBUG_MODE"));

//##########################################
// DEFINING GLOBAL PATH VARIABLES AND NAMES
//##########################################

// Path to the model and its lunch script
string model_sh   = emews_root + "/scripts/run-episim.sh";
string model_exec = emews_root + "/model/episim";

// string model_path = emews_root + "/model/EpiSim.jl";
// string model_exec = "julia --project=" model_path + " " + model_path + "/src/run.jl";

// Absolute path to files required by the model
string data_path  = turbine_output + "/data";

// Default base names for the model config file and the output folder
string base_config_name   = "config.json";
string base_output_folder = "output";
