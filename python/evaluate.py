import os
import json
import numpy as np
import pandas as pd
import xarray as xr
import xskillscore as xs


#################################################################
# Custom Evaluation Functions
#################################################################

def fit_epicurves(simdata_ds, instance_folder, data_folder, 
                  epidata_fname=None, epi_variable=None,
                  level='global', **kwargs):
    

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
    output_fname  = os.path.join(output_folder, kwargs["output_fname"])

    if level == 'global':
        col_pop = 'Total'
        epidata_xa = epidata_xa.sum(['G', 'M'])
        simdata_xa = simdata_xa.sum(['G', 'M'])
        epidata_xa = epidata_xa*scale/df_pop.loc[:,col_pop].sum()
        simdata_xa = simdata_xa*scale/df_pop.loc[:,col_pop].sum()
        rmse_xa = xs.rmse(simdata_xa, epidata_xa, dim = 'T')
        rmse_xa.to_netcdf(output_fname)
        return float(rmse_xa)

def dummy_evaluate(sim_xa, instance_folder, data_folder, **kwargs):
    return 0

#################################################################

evaluate_function_map = {
    "dummy_evaluate": dummy_evaluate,
    "fit_epicurves": fit_epicurves
}

def evaluate_obj(instance_folder, data_folder, workflow_config_fname):

    with open(workflow_config_fname) as fh:
        workflow_config = json.load(fh)
    output_folder = os.path.join(instance_folder, "output")

    evaluation_dict = workflow_config.get('evaluation', None)
    if evaluation_dict is None:
        raise Exception("Can't perform evalaute_obj missing key evalaute in workflow config")
    
    function_name   = evaluation_dict.get("function", None)
    parameters_dict = evaluation_dict.get("parameters", {})
    input_fname     =  evaluation_dict.get("input_fname", None)
    input_fname     = os.path.join(output_folder, input_fname)
    sim_ds = xr.load_dataset(input_fname)
    evaluate_function = evaluate_function_map[function_name]
    
    return evaluate_function(sim_ds, instance_folder, data_folder, **parameters_dict)

#################################################################
