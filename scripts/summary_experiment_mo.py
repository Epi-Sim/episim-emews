import glob
import pandas as pd
import xarray as xr
import xskillscore as xs
import json

experiment_folder = "test_deap_ga_mo"
level = "global"
prov = '02'
pattern = f"../experiments/{experiment_folder}/instance_*/output/RMSE_{level}.nc"

list_gen = []
list_ind = []

if level == 'global':
	list_RMSE_D = []
	list_RMSE_H = []
	for path in glob.glob(pattern):
	    split_path = path.split("/")
	    instance = split_path[3]
	    split_instance = instance.split("_")
	    generation = split_instance[1]
	    individual = split_instance[2]

	    rmse = xr.load_dataarray(path)
	    RMSE_D = rmse['new_deaths']
	    RMSE_H = rmse['new_hospitalized']
	    list_gen.append(float(generation))
	    list_ind.append(float(individual))
	    list_RMSE_D.append(float(RMSE_D))
	    list_RMSE_H.append(float(RMSE_H))
	    
	d = {'generation': list_gen,'individual': list_ind,
	     'RMSE_D': list_RMSE_D, 'RMSE_H': list_RMSE_H}

elif level == 'age':
	list_RMSE_Y_H = []
	list_RMSE_M_H = []
	list_RMSE_O_H = []
	list_RMSE_M_D = []
	list_RMSE_O_D = []
	for path in glob.glob(pattern):
	    split_path = path.split("/")
	    instance = split_path[3]
	    split_instance = instance.split("_")
	    generation = split_instance[1]
	    individual = split_instance[2]

	    rmse = xr.load_dataset(path)
	    Y_H = rmse['new_hospitalized'].loc['Y']
	    M_H = rmse['new_hospitalized'].loc['M']
	    D_H = rmse['new_hospitalized'].loc['O']
	    M_D = rmse['new_deaths'].loc['M']
	    O_D = rmse['new_deaths'].loc['O']
	    list_gen.append(float(generation))
	    list_ind.append(float(individual))
	    list_RMSE_Y_H.append(float(Y_H))
	    list_RMSE_M_H.append(float(M_H))
	    list_RMSE_O_H.append(float(O_H))
	    list_RMSE_M_D.append(float(M_D))
	    list_RMSE_O_D.append(float(O_D))
	    
	d = {'generation': list_gen,'individual': list_ind,'RMSE_Y_hosp': list_RMSE_Y_H,
		'RMSE_M_hosp': list_RMSE_M_H, 'RMSE_O_hosp': list_RMSE_O_H,
		'RMSE_M_death': list_RMSE_M_D, 'RMSE_O_death': list_RMSE_O_D}
		
elif level == 'prov':
	list_RMSE_D = []
	list_RMSE_H = []
	for path in glob.glob(pattern):
	    split_path = path.split("/")
	    instance = split_path[3]
	    split_instance = instance.split("_")
	    generation = split_instance[1]
	    individual = split_instance[2]

	    rmse = xr.load_dataset(path)
	    RMSE_D = rmse['new_deaths'].loc[prov]
	    RMSE_H = rmse['new_hospitalized'].loc[prov]
	    list_gen.append(float(generation))
	    list_ind.append(float(individual))
	    list_RMSE_D.append(float(RMSE_D))
	    list_RMSE_H.append(float(RMSE_H))
	    d = {'generation': list_gen,'individual': list_ind,
	     'RMSE_D': list_RMSE_D, 'RMSE_H': list_RMSE_H}
	    level = f'prov_{prov}'

elif level == 'prov_age'
	list_RMSE_Y_H = []
	list_RMSE_M_H = []
	list_RMSE_O_H = []
	list_RMSE_M_D = []
	list_RMSE_O_D = []
	for path in glob.glob(pattern):
	    split_path = path.split("/")
	    instance = split_path[3]
	    split_instance = instance.split("_")
	    generation = split_instance[1]
	    individual = split_instance[2]

	    rmse = xr.load_dataset(path)
	    Y_H = rmse['new_hospitalized'].loc[prov,'Y']
	    M_H = rmse['new_hospitalized'].loc[prov,'M']
	    D_H = rmse['new_hospitalized'].loc[prov,'O']
	    M_D = rmse['new_deaths'].loc[prov,'M']
	    O_D = rmse['new_deaths'].loc[prov,'O']
	    list_gen.append(float(generation))
	    list_ind.append(float(individual))
	    list_RMSE_Y_H.append(float(Y_H))
	    list_RMSE_M_H.append(float(M_H))
	    list_RMSE_O_H.append(float(O_H))
	    list_RMSE_M_D.append(float(M_D))
	    list_RMSE_O_D.append(float(O_D))
	    level = f'prov_{prov}'
	    
	d = {'generation': list_gen,'individual': list_ind,'RMSE_Y_hosp': list_RMSE_Y_H,
		'RMSE_M_hosp': list_RMSE_M_H, 'RMSE_O_hosp': list_RMSE_O_H,
		'RMSE_M_death': list_RMSE_M_D, 'RMSE_O_death': list_RMSE_O_D}	

df = pd.DataFrame(data = d)

#df = df.sort_values(by=['RMSE_M_death', 'RMSE_O_death', 'RMSE_Y_hosp'])

output_path = f"../experiments/{experiment_folder}/summary_{level}.csv"
df.to_csv(output_path, index=False)   
