import os
import json
import numpy as np
import pandas as pd
import xarray as xr
import xskillscore as xs
from postprocessing import scale_by_population
from metapopulation import Metapopulation

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

    scale_by_population(epidata_xa, instance_folder, data_folder, scale=1e5, level=level)
    scale_by_population(simdata_xa, instance_folder, data_folder, scale=1e5, level=level)
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

    scale_by_population(epidata_xa, instance_folder, data_folder, scale=1e5, level=level)
    scale_by_population(simdata_xa, instance_folder, data_folder, scale=1e5, level=level)
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


#################################################################


def fit_epicurves(
    sim_ds,
    instance_folder,
    data_folder,
    obsdata_fname="real_observables.nc",
    epi_variable="new_deaths",
    metric="rmse",
    smooth_obs=True,
    scale_by_pop=True,
    agg_level="level_2",
    agg_func="sum",
    weight_by_population=False,
    scale_factor=1e5,
    varlist = ['new_infected', 'new_hospitalized', 'new_deaths'],
    epsilon = 1e-9
):
    """
    Compute a fitting score between simulated and observed epidemic curves.

    Parameters
    ----------
    sim_ds : xarray.Dataset
        Simulated epidemic data including time (`T`) and variables such as 'new_infected', 'new_hospitalized', 'new_deaths'.
    instance_folder : str
        Path to the simulation instance folder containing the 'config.json' file.
    data_folder : str
        Path to the folder containing observational data files like 'real_observables.nc' and 'rosetta.csv'.
    epivar : str, default="new_deaths"
        Name of the epidemic variable to evaluate (e.g., "new_deaths", "new_infected").
    metric : str, default="rmse"
        Error metric to use for comparison. Options: "rmse", "mape".
    smooth_obs : bool, default=True
        Whether to apply a 7-day rolling average to observational data.
    scale_by_pop : bool, default=True
        Whether to scale observed and simulated values by population (per capita).
    agg_level : str, default="level_2"
        Spatial aggregation level used to align data across regions.
    weight_by_population : bool, default=False
        Whether to apply population-weighted aggregation of error metrics.
    scale_factor : float, default=1e5
        Scaling factor used when applying population weights (e.g., to report per 100,000).

    Returns
    -------
    float
        Aggregated fitting score based on the chosen metric and epidemic variable.
    """

    # Load simulation configuration
    config_path = os.path.join(instance_folder, "config.json")
    with open(config_path) as fh:
        config_dict = json.load(fh)

    # Extract time bounds
    start_date = config_dict['simulation']['start_date']
    end_date = config_dict['simulation']['end_date']

    # Load observed epidemic data
    obs_path = os.path.join(data_folder, obsdata_fname)
    obs_ds = xr.load_dataset(obs_path)

    # Apply optional smoothing (7-day rolling mean)
    if smooth_obs:
        obs_ds = obs_ds.rolling(T=7, center=True, min_periods=1).mean()

    # Ensure datetime types and clip to simulation period
    sim_ds['T'] = pd.to_datetime(sim_ds['T'].values)
    sim_ds = sim_ds.sel(T=slice(start_date, end_date))

    obs_ds['T'] = pd.to_datetime(obs_ds['T'].values)
    obs_ds = obs_ds.sel(T=slice(start_date, end_date))
    
    # Keep only relevant variables
    sim_ds = sim_ds[varlist]
    obs_ds = obs_ds[varlist]

    # Align time and space
    obs_ds, sim_ds = xr.align(obs_ds, sim_ds)

    if epi_variable not in varlist:
        raise ValueError(f"Unsupported epivar: {epi_variable}. Use: ", varlist)

    # Load population data
    pop_fname = config_dict["data"]["metapopulation_data_filename"]
    metapop_csv = os.path.join(data_folder, pop_fname)
    rosetta_csv = os.path.join(data_folder, "rosetta.csv")
    metapop = Metapopulation(metapop_csv, rosetta_csv=rosetta_csv)
    pop_da = metapop.aggregate_to_level(agg_level)

    # Optionally scale values by population
    if scale_by_pop:
        obs_ds = obs_ds / pop_da
        sim_ds = sim_ds / pop_da

    # Compute error metric
    if metric == "rmse":
        cost_ds = xs.rmse(obs_ds, sim_ds, dim="T")
    elif metric == "mape":
        cost_ds = xs.mape(obs_ds, sim_ds+epsilon, dim="T")
    elif metric == "mae":
        cost_ds = xs.mae(obs_ds, sim_ds+epsilon, dim="T")
    else:
        raise ValueError(f"Unsupported metric: {metric}. Use 'rmse', 'mape' or 'mae.")

    # Apply optional population-weighting to the error values
    if weight_by_population:
        pop_weights_da = pop_da / pop_da.sum()
        cost_ds, pop_weights_da = xr.align(cost_ds, pop_weights_da)
        cost_ds = cost_ds * pop_weights_da * scale_factor

    # Return the summed metric for the specified epidemic variable
    if agg_func == "sum":
        return float(cost_ds[epi_variable].sum())
    elif agg_func == "mean":
        return float(cost_ds[epi_variable].mean())
    else:
        raise ValueError(f"Unsupported agg_func: {agg_func}. Use 'sum' or 'mean'.")



def dummy_evaluate(simdata_ds, instance_folder, data_folder, **kwargs):
    return -1

#################################################################

evaluate_function_map = {
    "dummy_evaluate": dummy_evaluate,
    "fit_epicurves": fit_epicurves,
}

def evaluate_obj(instance_folder, data_folder, workflow_config_fname):

    with open(workflow_config_fname) as fh:
        workflow_config = json.load(fh)
    output_folder = os.path.join(instance_folder, "output")

    evaluation_dict = workflow_config.get('evaluation', None)
    if evaluation_dict is None:
        raise Exception("Error: Can't perform evaluate_obj missing key evaluate entry in workflow config")

    function_name   = evaluation_dict.get("function", None)
    evaluate_function = evaluate_function_map.get(function_name, None)
    if evaluate_function is None:
        raise Exception(f"Error: evaluate_function \"{function_name}\" not defined in evaluate_function_map")


    parameters_dict = evaluation_dict.get("parameters", {})
    input_fname     = evaluation_dict.get("input_fname", None)
    input_fname     = os.path.join(output_folder, input_fname)
    sim_ds = xr.load_dataset(input_fname)
    
    cost = evaluate_function(sim_ds, instance_folder, data_folder, **parameters_dict)
        
    return cost

#################################################################
