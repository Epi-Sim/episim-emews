import glob
import pandas as pd
import xarray as xr
import xskillscore as xs
import json
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import datetime

base_folder = ".."
experiment_folder = "test_deap_cmaes"
pattern = f"{base_folder}/experiments/{experiment_folder}/instance_*/output/RMSE.nc"

#ANALYZE THE FULL EXPERIMENT LOOKING FOR THE BEST SIMULATION (min RMSE)

list_gen = []
list_ind = []
list_RMSE = []

for path in glob.glob(pattern):
    split_path = path.split("/")
    instance = split_path[3]
    split_instance = instance.split("_")
    generation = split_instance[1]
    individual = split_instance[2]

    xa = xr.load_dataarray(path)
    list_gen.append(float(generation))
    list_ind.append(float(individual))
    list_RMSE.append(float(xa))
    
d = {'generation': list_gen,'individual': list_ind,'RMSE': list_RMSE}
df = pd.DataFrame(data = d)

df = df.sort_values(by='RMSE')

output_path = f"{base_folder}/experiments/{experiment_folder}/summary.csv"
df.to_csv(output_path, index=False)

