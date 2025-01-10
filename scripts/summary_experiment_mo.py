import glob
import pandas as pd
import xarray as xr
import xskillscore as xs
import json

experiment_folder = "test_deap_ga_mo"
pattern = f"../experiments/{experiment_folder}/instance_*/output/RMSE.nc"

list_gen = []
list_ind = []
list_RMSE_Y_H = []
list_RMSE_M_D = []
list_RMSE_O_D = []

for path in glob.glob(pattern):
    split_path = path.split("/")
    instance = split_path[3]
    split_instance = instance.split("_")
    generation = split_instance[1]
    individual = split_instance[2]

    rmse = xr.load_dataset(path)
    #Y_H = rmse['new_hospitalized'].loc['Y']
    Y_H = rmse['new_hospitalized'].loc['Y']
    M_D = rmse['new_deaths'].loc['M']
    O_D = rmse['new_deaths'].loc['O']
    list_gen.append(float(generation))
    list_ind.append(float(individual))
    list_RMSE_Y_H.append(float(Y_H))
    list_RMSE_M_D.append(float(M_D))
    list_RMSE_O_D.append(float(O_D))
    
d = {'generation': list_gen,'individual': list_ind,'RMSE_Y_hosp': list_RMSE_Y_H,
	'RMSE_M_death': list_RMSE_M_D, 'RMSE_O_death': list_RMSE_O_D}
df = pd.DataFrame(data = d)

df = df.sort_values(by=['RMSE_M_death', 'RMSE_O_death', 'RMSE_Y_hosp'])

output_path = f"../experiments/{experiment_folder}/summary.csv"
df.to_csv(output_path, index=False)   
