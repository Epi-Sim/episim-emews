import os
import json
import numpy as np
import pandas as pd
import xarray as xr
import xskillscore as xs
import episim_utils


def _aggregate_patches(sim_xa, patch_mapping=None):
    if patch_mapping is None:
        return sim_xa.sum("M")

    if len(sim_xa.dims) == 4:
        dims = ['G', 'M', 'T', 'V']
        sim_xa = sim_xa.transpose(*dims)
        nda_list = []
        for i in patch_mapping.keys():
            nda = sim_xa.loc[:, patch_mapping[i], :].sum("M").values
            nda_list.append(nda)
        data = np.stack(nda_list)
        data = data.transpose(1, 0, 2, 3)
    elif len(sim_xa.dims) == 3:
        dims = ['G', 'M', 'T']
        sim_xa = sim_xa.transpose(*dims)
        nda_list = []
        for i in patch_mapping.keys():
            nda = sim_xa.loc[:, patch_mapping[i], :].sum("M").values
            nda_list.append(nda)
        data = np.stack(nda_list)
        data = data.transpose(1, 0, 2)
    else:
        raise Exception(f"Wrong dimenssion for data array.\
                        Expecting 3 or 4 recieved {len(sim_xa.dims)}")

    new_coords = {}
    for dim in sim_xa.dims:
        new_coords[dim] = sim_xa.coords[dim]

    new_coords["M"] =  list(patch_mapping)
    return xr.DataArray(data=data, coords=new_coords, dims=sim_xa.dims)

def aggregate_patches(sim_ds, instance_folder, data_folder, mapping_fname="rosetta.csv", **kwargs):
    patch_mapping = None
    mapping_fname = os.path.join(data_folder, mapping_fname)
    if os.path.exists(mapping_fname):
        df = pd.read_csv(mapping_fname, dtype=str)
        patch_mapping = {i: df.loc[df["level_2"]==i, "level_1"].tolist() for i in df["level_2"].unique()}


    data_vars = {}
    for var in sim_ds:
        data_vars[var] = _aggregate_patches(sim_ds[var], patch_mapping)

    coords = data_vars[var].coords
    return xr.Dataset(data_vars=data_vars, coords=coords)


def RMSE_global(obs_ds, sim_ds, metapop_csv, rosetta_csv):
    agg_level = 'level_4'
    metapop = episim_utils.Metapopulation(metapop_csv, rosetta_csv=rosetta_csv)
    pop_da = metapop.aggregate_to_level(agg_level)
    
    pop_da = pop_da.sum(['G', 'M'])
    obs_ds = obs_ds.sum(['G', 'M'])
    sim_ds = sim_ds.sum(['G', 'M'])

    return pop_da, obs_ds, sim_ds

def RMSE_g(obs_ds, sim_ds, metapop_csv, rosetta_csv):
    agg_level = 'level_4'
    metapop = episim_utils.Metapopulation(metapop_csv, rosetta_csv=rosetta_csv)
    pop_da = metapop.aggregate_to_level(agg_level)

    pop_da = pop_da.sum(['M'])
    obs_ds = obs_ds.sum(['M'])
    sim_ds = sim_ds.sum(['M'])

    return pop_da, obs_ds, sim_ds

def RMSE_m(obs_ds, sim_ds, metapop_csv, rosetta_csv):
    agg_level = 'level_2'
    metapop = episim_utils.Metapopulation(metapop_csv, rosetta_csv=rosetta_csv)
    pop_da = metapop.aggregate_to_level(agg_level)

    pop_da = pop_da.sum(['G'])
    obs_ds = obs_ds.sum(['G'])
    sim_ds = sim_ds.sum(['G'])

    return pop_da, obs_ds, sim_ds

def RMSE_mg(obs_ds, sim_ds, metapop_csv, rosetta_csv):
    agg_level = 'level_2'
    metapop = episim_utils.Metapopulation(metapop_csv, rosetta_csv=rosetta_csv)
    pop_da = metapop.aggregate_to_level(agg_level)

    return pop_da, obs_ds, sim_ds


def compute_RMSEs(
    sim_ds,
    instance_folder,
    data_folder,
    obsdata_fname="real_observables.nc",
    epivariable_weights={"new_deaths": 1},
    metric="rmse",
    smooth_obs=True,
    scale_by_pop=True,
    agg_level="level_2",
    agg_func="sum",
    weight_by_population=False,
    scale_factor=1e5,
    varlist = ['new_infected', 'new_hospitalized', 'new_deaths'],
    epsilon = 1e-9,
    **kwargs
):
    """
    Compute a fitting score between simulated and observed epidemic curves.

    Parameters
    ----------
    sim_ds : xarray.Dataset
        Simulated epidemic data including time (`T`) and variables such as 'new_infected', 'new_hospitalized', 'new_deaths'.
    instance_folder : str
        Path to the simulation instance folder containing the 'episim_config.json' file.
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
    config_path = os.path.join(instance_folder, "episim_config.json")
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
    sim_input = sim_ds.copy()
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

    sim_aux = sim_ds.copy()
    obs_aux = obs_ds.copy()

    for k in epivariable_weights:
        if k in varlist:
            continue
        raise ValueError(f"Unsupported epivar: {k}. Use: ", varlist)

    # Load population data
    pop_fname = config_dict["data"]["metapopulation_data_filename"]
    metapop_csv = os.path.join(data_folder, pop_fname)
    rosetta_csv = os.path.join(data_folder, "rosetta.csv")


    functions = [RMSE_global, RMSE_g, RMSE_m, RMSE_mg]
    
    costs = {}
    for f in functions:

        pop_da, obs_ds, sim_ds = f(obs_aux, sim_aux, metapop_csv, rosetta_csv)

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
            cost_ds = cost_ds.sum()
        elif agg_func == "mean":
            cost_ds = cost_ds.mean()
        else:
            raise ValueError(f"Unsupported agg_func: {agg_func}. Use 'sum' or 'mean'.")

        cost = 0
        for k,v in epivariable_weights.items():
            cost += float(cost_ds[k] * v)
        costs[f.__name__] = cost

        output_fname = os.path.join(instance_folder, "output/RMSEs.json")
        
        with open(output_fname, 'w') as f1:
            json.dump(costs, f1, indent=2)

    return sim_input

def scale_by_population(sim_ds, instance_folder, data_folder, level='prov_age', scale=1e5, **kwargs):

     #The data has to be in xarray.DataSet format
    
    config_fname = os.path.join(instance_folder, "episim_config")
    with open(config_fname) as fh:
        config_dict = json.load(fh)

    G_labels = config_dict['population_params']['G_labels']
    #pop_fname = config_dict['data']["metapopulation_data_filename"]
    pop_fname = os.path.join(data_folder, 'metapopulation_data_prov.csv')
    pop_df = pd.read_csv(pop_fname, dtype={'id':'str'})
    pop_df = pop_df.set_index('id')
    pop_df = pop_df[G_labels].stack()
    pop_df.index.names = ('M', 'G')
    pop_xa = pop_df.to_xarray()
    if level == 'global':
        pop_xa = pop_xa.sum(['M','G'])
        for var in sim_ds:
            sim_ds[var] = sim_ds[var] / pop_xa * scale
        return sim_ds    
    elif level == 'age':
        pop_xa = pop_xa.sum(['M'])
        for var in sim_ds:
            sim_ds[var] = sim_ds[var] / pop_xa * scale
        return sim_ds
    elif level == 'prov':
        pop_xa = pop_xa.sum(['G'])
        for var in sim_ds:
            sim_ds[var] = sim_ds[var] / pop_xa * scale
        return sim_ds
    elif level == 'prov_age':
        for var in sim_ds:
            sim_ds[var] = sim_ds[var] / pop_xa * scale
        return sim_ds
    elif level == 'one_prov':
        region = kwargs['region']
        pop_xa = pop_xa.sel(M=region).drop_vars('M').sum(['G'])
        for var in sim_ds:
            sim_ds[var] = sim_ds[var] / pop_xa * scale
        return sim_ds
    elif level == 'one_prov_age':
        region = kwargs['region']
        pop_xa = pop_xa.sel(M=region).drop_vars('M')
        for var in sim_ds:
            sim_ds[var] = sim_ds[var] / pop_xa * scale
        return sim_ds
    else :
        return "error"


"""
Example of a correct postprocessing function defintion
the function should acept the following arguments
- sim_ds: xarray with simulation output
- instance_folder: string (path to the instance folder)
- data_folder: string (path to the data folder)
- **kwargs: dict (additional arguments as key:value pairs)
"""
def dummy_postprocessing(sim_ds, instance_folder, data_folder, **kwargs):
    return sim_ds


postprocessing_map = {
    "dummy_postprocessing": dummy_postprocessing,
    "scale_by_population": scale_by_population,
    "aggregate_simulation": aggregate_patches,
    "compute_RMSEs": compute_RMSEs
}

def postprocess_obj(instance_folder, data_folder, workflow_config_fname):

    with open(workflow_config_fname) as fh:
        workflow_config = json.load(fh)
    
    postprocess_params = workflow_config.get('postprocessing', None)
    if postprocess_params is None:
        raise Exception("Can't perform postprocess_obj missing key \"postprocessing\" in workflow config")

    output_folder = os.path.join(instance_folder, "output")
    input_fname   = os.path.join(output_folder, postprocess_params["input_fname"])
    output_fname  = os.path.join(output_folder, postprocess_params["output_fname"])
    
    sim_ds = xr.load_dataset(input_fname)    
    for step in postprocess_params['steps']:
        func_name = step['function'] 
        postprocessing_step = postprocessing_map[func_name]
        sim_ds = postprocessing_step(sim_ds, instance_folder, data_folder, **step)

    if postprocess_params["remove_input"]:
        os.remove(input_fname)
    
    sim_ds.to_netcdf(output_fname)
    
    return output_fname
 




