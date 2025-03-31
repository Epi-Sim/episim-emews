import glob
import pandas as pd
import xarray as xr
import xskillscore as xs
import json

experiment_folder = "test_deap_cmaes_mo_prueba"
level = "global"
prov = '02'
metric = 'MAPE'
pattern = f"../experiments/{experiment_folder}/instance_*/output/{metric}_{level}.nc"

list_gen = []
list_ind = []

if level == 'global':
	list_D = []
	list_H = []
	for path in glob.glob(pattern):
	    split_path = path.split("/")
	    instance = split_path[3]
	    split_instance = instance.split("_")
	    generation = split_instance[1]
	    individual = split_instance[2]

	    metric_xa = xr.load_dataset(path)
	    metric_D = metric_xa['new_deaths']
	    metric_H = metric_xa['new_hospitalized']
	    list_gen.append(float(generation))
	    list_ind.append(float(individual))
	    list_D.append(float(metric_D))
	    list_H.append(float(metric_H))
	if metric == 'RMSE': 
		d = {'generation': list_gen,'individual': list_ind,
	     	'RMSE_D': list_D, 'RMSE_H': list_H}
	elif metric == 'MAPE':
		d = {'generation': list_gen,'individual': list_ind,
	     	'MAPE_D': list_D, 'MAPE_H': list_H}

elif level == 'age':
	list_Y_H = []
	list_M_H = []
	list_O_H = []
	list_M_D = []
	list_O_D = []
	for path in glob.glob(pattern):
	    split_path = path.split("/")
	    instance = split_path[3]
	    split_instance = instance.split("_")
	    generation = split_instance[1]
	    individual = split_instance[2]

	    metric_xa = xr.load_dataset(path)
	    Y_H = metric_xa['new_hospitalized'].loc['Y']
	    M_H = metric_xa['new_hospitalized'].loc['M']
	    O_H = metric_xa['new_hospitalized'].loc['O']
	    M_D = metric_xa['new_deaths'].loc['M']
	    O_D = metric_xa['new_deaths'].loc['O']
	    list_gen.append(float(generation))
	    list_ind.append(float(individual))
	    list_Y_H.append(float(Y_H))
	    list_M_H.append(float(M_H))
	    list_O_H.append(float(O_H))
	    list_M_D.append(float(M_D))
	    list_O_D.append(float(O_D))
	
	if metric == 'RMSE':	    
	    d = {'generation': list_gen,'individual': list_ind,'RMSE_Y_hosp': list_Y_H,
		'RMSE_M_hosp': list_M_H, 'RMSE_O_hosp': list_O_H,
		'RMSE_M_death': list_M_D, 'RMSE_O_death': list_O_D}
	elif metric == 'MAPE':	    
	    d = {'generation': list_gen,'individual': list_ind,'MAPE_Y_hosp': list_Y_H,
		'MAPE_M_hosp': list_M_H, 'MAPE_O_hosp': list_O_H,
		'MAPE_M_death': list_M_D, 'MAPE_O_death': list_O_D}
		
elif level == 'prov':
	list_D = []
	list_H = []
	for path in glob.glob(pattern):
	    split_path = path.split("/")
	    instance = split_path[3]
	    split_instance = instance.split("_")
	    generation = split_instance[1]
	    individual = split_instance[2]

	    metric_xa = xr.load_dataset(path)
	    metric_D = metric_xa['new_deaths'].loc[prov]
	    metric_H = metric_xa['new_hospitalized'].loc[prov]
	    list_gen.append(float(generation))
	    list_ind.append(float(individual))
	    list_D.append(float(metric_D))
	    list_H.append(float(metric_H))
	    
	if metric == 'RMSE':
	    d = {'generation': list_gen,'individual': list_ind,
	     'RMSE_D': list_D, 'RMSE_H': list_H}
	elif metric == 'MAPE':
	    d = {'generation': list_gen,'individual': list_ind,
	     'MAPE_D': list_D, 'MAPE_H': list_H}
	level = f'prov_{prov}'

elif level == 'prov_age':
	list_Y_H = []
	list_M_H = []
	list_O_H = []
	list_M_D = []
	list_O_D = []
	for path in glob.glob(pattern):
	    split_path = path.split("/")
	    instance = split_path[3]
	    split_instance = instance.split("_")
	    generation = split_instance[1]
	    individual = split_instance[2]

	    metric_xa = xr.load_dataset(path)
	    Y_H = metric_xa['new_hospitalized'].loc[prov,'Y']
	    M_H = metric_xa['new_hospitalized'].loc[prov,'M']
	    O_H = metric_xa['new_hospitalized'].loc[prov,'O']
	    M_D = metric_xa['new_deaths'].loc[prov,'M']
	    O_D = metric_xa['new_deaths'].loc[prov,'O']
	    list_gen.append(float(generation))
	    list_ind.append(float(individual))
	    list_Y_H.append(float(Y_H))
	    list_M_H.append(float(M_H))
	    list_O_H.append(float(O_H))
	    list_M_D.append(float(M_D))
	    list_O_D.append(float(O_D))
	if metric == 'RMSE':    
	    d = {'generation': list_gen,'individual': list_ind,'RMSE_Y_hosp': list_Y_H,
		'RMSE_M_hosp': list_M_H, 'RMSE_O_hosp': list_O_H,
		'RMSE_M_death': list_M_D, 'RMSE_O_death': list_O_D}
	elif metric == 'MAPE':    
	    d = {'generation': list_gen,'individual': list_ind,'MAPE_Y_hosp': list_Y_H,
		'MAPE_M_hosp': list_M_H, 'MAPE_O_hosp': list_O_H,
		'MAPE_M_death': list_M_D, 'MAPE_O_death': list_O_D}
        #level = f'prov_{prov}'

df = pd.DataFrame(data = d)

#df = df.sort_values(by=['RMSE_M_death', 'RMSE_O_death', 'RMSE_Y_hosp'])

output_path = f"../experiments/{experiment_folder}/summary_{metric}_{level}.csv"
df.to_csv(output_path, index=False)   
