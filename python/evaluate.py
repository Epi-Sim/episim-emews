import os
import json
import numpy as np
import pandas as pd
import xarray as xr
import xskillscore as xs
from postprocessing import scale_by_population

#################################################################
# Custom Evaluation Functions
#################################################################
def compute_MAPE(simdata_ds, instance_folder, data_folder, epidata_fname=None,
                 epi_variable=['new_hospitalized', 'new_deaths'], level='global',
                 **kwargs):
    config_fname = os.path.join(instance_folder, "config.json")
    with open(config_fname) as fh:
        config_dict = json.load(fh)
    
    start_date = config_dict['simulation']['start_date']
    end_date = config_dict['simulation']['end_date']

    pop_fname = config_dict["data"]["metapopulation_data_filename"]
    pop_fname = os.path.join(data_folder, pop_fname)

    df_pop = pd.read_csv(pop_fname)

    scale = kwargs["scale"]

    epidata_fname = os.path.join(data_folder, epidata_fname)
    epidata_ds = xr.load_dataset(epidata_fname)

    epidata_ds['T'] = pd.DatetimeIndex(epidata_ds['T'].values)
    epidata_ds = epidata_ds.sel(T=slice( start_date,end_date))
    simdata_ds['T'] = pd.DatetimeIndex(simdata_ds['T'].values)
    
    epidata_xa = epidata_ds[epi_variable]
    simdata_xa = simdata_ds[epi_variable]

    output_folder = os.path.join(instance_folder, "output")
    output_fname  = os.path.join(output_folder, f"MAPE_{level}.nc")

    if level == 'global':
        epidata_xa = epidata_xa.sum(['G', 'M'])
        simdata_xa = simdata_xa.sum(['G', 'M'])
    elif level == 'age':
        epidata_xa = epidata_xa.sum(['M'])
        simdata_xa = simdata_xa.sum(['M'])
    elif level == 'prov':
        epidata_xa = epidata_xa.sum(['G'])
        simdata_xa = simdata_xa.sum(['G'])
    elif level == 'prov_age':
        epidata_xa = epidata_xa
        simdata_xa = simdata_xa
    else:
        return "ERROR EVALUATE"
    
    epidata_xa = epidata_xa + 1
    simdata_xa = simdata_xa + 1

    scale_by_population(epidata_xa, instance_folder, data_folder, scale=scale, level=level)
    scale_by_population(simdata_xa, instance_folder, data_folder, scale=scale, level=level)
    mape_xa = xs.mape(epidata_xa, simdata_xa, dim = 'T')
    mape_xa.to_netcdf(output_fname)
    return mape_xa

def compute_RMSE(simdata_ds, instance_folder, data_folder, epidata_fname=None,
                 epi_variable=['new_hospitalized', 'new_deaths'], level='global',
                 **kwargs):
    config_fname = os.path.join(instance_folder, "config.json")
    with open(config_fname) as fh:
        config_dict = json.load(fh)
    
    start_date = config_dict['simulation']['start_date']
    end_date = config_dict['simulation']['end_date']

    pop_fname = config_dict["data"]["metapopulation_data_filename"]
    pop_fname = os.path.join(data_folder, pop_fname)

    df_pop = pd.read_csv(pop_fname)

    scale = kwargs["scale"]

    epidata_fname = os.path.join(data_folder, epidata_fname)
    epidata_ds = xr.load_dataset(epidata_fname)

    epidata_ds['T'] = pd.DatetimeIndex(epidata_ds['T'].values)
    epidata_ds = epidata_ds.sel(T=slice( start_date,end_date))
    simdata_ds['T'] = pd.DatetimeIndex(simdata_ds['T'].values)
    
    epidata_xa = epidata_ds[epi_variable]
    simdata_xa = simdata_ds[epi_variable]

    output_folder = os.path.join(instance_folder, "output")
    output_fname  = os.path.join(output_folder, f"RMSE_{level}.nc")

    if level == 'global':
        epidata_xa = epidata_xa.sum(['G', 'M'])
        simdata_xa = simdata_xa.sum(['G', 'M'])
    elif level == 'age':
        epidata_xa = epidata_xa.sum(['M'])
        simdata_xa = simdata_xa.sum(['M'])
    elif level == 'prov':
        epidata_xa = epidata_xa.sum(['G'])
        simdata_xa = simdata_xa.sum(['G'])
    elif level == 'prov_age':
        epidata_xa = epidata_xa
        simdata_xa = simdata_xa
    else:
        return "ERROR EVALUATE"

    scale_by_population(epidata_xa, instance_folder, data_folder, scale=scale, level=level)
    scale_by_population(simdata_xa, instance_folder, data_folder, scale=scale, level=level)
    rmse_xa = xs.rmse(epidata_xa, simdata_xa, dim = 'T')
    rmse_xa.to_netcdf(output_fname)
    return rmse_xa

def fit_objectives(instance_folder, num_objectives, parameters,  **kwargs):
    metric_list = []
    for i in range(int(num_objectives)):
        level = parameters[i]['level']
        metric = parameters[i]['metric']
        epi_variable = parameters[i]['epi_variable']
        metric_fname = os.path.join(instance_folder, f"output/{metric}_{level}.nc")
        metric_ds = xr.load_dataset(metric_fname)
        metric_xa = metric_ds[epi_variable]

        
        if level == 'global':
            metric_list.append(float(metric_xa))
        elif level == 'age':
            age = parameters[i]['G']
            metric_list.append(float(metric_xa.loc[age]))
        elif level == 'prov':
            prov = parameters[i]['M']
            metric_list.append(float(metric_xa.loc[prov]))
        elif level == 'prov_age':
            age = parameters[i]['G']
            prov = parameters[i]['M']
            metric_list.append(float(metric_xa.loc[prov,age]))
        else:
            return "ERROR SELECT FITNESS"
    metric_list = ','.join(map(str,metric_list))
    return metric_list

def dummy_evaluate(instance_folder, **kwargs):
    return 0

#################################################################

evaluate_function_map = {
    "dummy_evaluate": dummy_evaluate,
    "compute_RMSE": compute_RMSE,
    "compute_MAPE": compute_MAPE,
    "fit_objectives": fit_objectives
}

def evaluate_obj(instance_folder, data_folder, workflow_config_fname):

    with open(workflow_config_fname) as fh:
        workflow_config = json.load(fh)
    output_folder = os.path.join(instance_folder, "output")

    evaluation_dict = workflow_config.get('evaluation', None)
    if evaluation_dict is None:
        raise Exception("Can't perform evalaute_obj missing key evalaute in workflow config")

    for step in evaluation_dict["steps"]:
        function_name   = step["function"]
        input_fname     =  step.get("input_fname", None)
        parameters_dict = step.get("parameters", {})       
    
        evaluate_function = evaluate_function_map[function_name]  
        if input_fname:
            input_fname = os.path.join(output_folder, input_fname)
            sim_ds = xr.load_dataset(input_fname)
            evaluate_function(sim_ds, instance_folder, data_folder, **parameters_dict)
        else:
            fitness = evaluate_function(instance_folder, **parameters_dict)
        
    return fitness

#################################################################
