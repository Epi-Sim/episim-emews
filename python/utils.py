import os
import json
import numpy as np
import pandas as pd


def update_params(params_dict, update_dict):
    G = 3
    # Mapping epi_param βᴵ
    if "βᴵ" in update_dict:
        params_dict["epidemic_params"]["βᴵ"] = update_dict["βᴵ"]
    elif "β" in update_dict:
        params_dict["epidemic_params"]["βᴵ"] = update_dict["β"]
   # Mapping epi_param βᴬ
    if "βᴬ" in update_dict:
        params_dict["epidemic_params"]["βᴬ"] = update_dict["βᴬ"]
    elif "scale_β" in update_dict:
        params_dict["epidemic_params"]["βᴬ"] = params_dict["epidemic_params"]["βᴵ"] * update_dict["scale_β"]
    # Mapping epi_param ηᵍ
    if "ηᵍ" in update_dict:
        x = update_dict["ηᵍ"]
        params_dict["epidemic_params"]["ηᵍ"] = [x, x, x]
    elif ("τ_inc" in update_dict) and ("scale_ea" in update_dict):
        t_inc = update_dict["τ_inc"]
        s_ea = update_dict["scale_ea"]
        nu_g = 1.0/(t_inc * (1.0 - s_ea))
        params_dict["epidemic_params"]["ηᵍ"] = [nu_g] * G
    if "ηᵍY" in update_dict:
        params_dict["epidemic_params"]["ηᵍ"] = [update_dict["ηᵍY"], update_dict["ηᵍM"], update_dict["ηᵍO"]]
    # Mapping epi_param αᵍ
    if "αᵍ" in update_dict:
        a = update_dict["αᵍ"]
        a1 = a/2.5
        params_dict["epidemic_params"]["αᵍ"] = [a1, a, a]
    elif ("τ_inc" in update_dict) and ("scale_ea" in update_dict) and ("τᵢ" in update_dict):
        t_inc = update_dict["τ_inc"]
        s_ea = update_dict["scale_ea"]
        ti = update_dict["τᵢ"]
        n1 = 1.0/(ti - 1 + t_inc * s_ea)
        n2 = 1.0/(t_inc * s_ea)
        n3 = 1.0/(t_inc * s_ea)
        params_dict["epidemic_params"]["αᵍ"] = [n1, n2, n3]
    if "αᵍY" in update_dict:
        params_dict["epidemic_params"]["αᵍ"] = [update_dict["αᵍY"], update_dict["αᵍM"], update_dict["αᵍO"]]

    # Mapping epi_param μᵍ
    if "μᵍ" in update_dict:
        u = update_dict["μᵍ"]
        params_dict["epidemic_params"]["μᵍ"] = [1,u,u]
    elif "τᵢ" in update_dict:
        ti = update_dict["τᵢ"]
        params_dict["epidemic_params"]["μᵍ"] = [1.0, 1.0/ti, 1.0/ti]
    if "μᵍY" in update_dict:
        params_dict["epidemic_params"]["μᵍ"] = [update_dict["μᵍY"], update_dict["μᵍM"], update_dict["μᵍO"]]
    
    #arreglar esto
    if "ϕs" in update_dict:
        if isinstance(update_dict["ϕs"],list):
            params_dict["NPI"]["ϕs"] = update_dict["ϕs"]
        else:
            params_dict["NPI"]["ϕs"] = [update_dict["ϕs"]]
    
    if "ϕs1" in update_dict:
        params_dict["NPI"]["ϕs"] = [update_dict["ϕs1"], update_dict["ϕs2"], update_dict["ϕs3"], update_dict["ϕs4"]]
    
    if "δs" in update_dict:
        if isinstance(update_dict["δs"],list):
            params_dict["NPI"]["δs"] = update_dict["δs"]
        else:
            params_dict["NPI"]["δs"] = [update_dict["δs"]]
    
    if "δs1" in update_dict:
        params_dict["NPI"]["δs"] = [update_dict["δs1"], update_dict["δs2"], update_dict["δs3"], update_dict["δs4"]]
    

    if "initial_condition_filename" in update_dict:
        params_dict["data"]["initial_condition_filename"] = update_dict["initial_condition_filename"]
    

    if "ϵᵍ" in update_dict:
        params_dict["vaccination"]["ϵᵍ"] = update_dict["ϵᵍ"]

    if "percentage_of_vacc_per_day" in update_dict:
        params_dict["vaccination"]["percentage_of_vacc_per_day"] = update_dict["percentage_of_vacc_per_day"]
    
    if "start_vacc" in update_dict:
        params_dict["vaccination"]["start_vacc"] = update_dict["start_vacc"]
    
    if "dur_vacc" in update_dict:
        params_dict["vaccination"]["dur_vacc"] = update_dict["dur_vacc"]


    return params_dict

def compute_observables(sim_xa, instance_folder, data_folder, **kwargs):
    """
    new_infectᵍ(t+1) = A(t) * αᵍ

    hosp_rateᵍ = μᵍ * (1 - θᵍ) * γᵍ
    new_hosptᵍ(t+1)  = I(t) * hosp_rateᵍ
    """

    observable_labels = ['A', 'I', 'D']

    config_fname = os.path.join(instance_folder, "config.json")

    with open(config_fname) as fh:
        config_dict = json.load(fh)
        
    G_labels  = config_dict['population_params']['G_labels']
    epi_params = config_dict['epidemic_params']
    
    sim_observables_xa = sim_xa.loc[:, :, :, observable_labels]
    sim_observables_xa = sim_observables_xa.transpose('epi_states', 'M', 'T', 'G')
    
    alphas     = np.zeros(len(G_labels))
    hosp_rates = np.zeros(len(G_labels))
    for i,g in enumerate(G_labels):
        alphas[i]     = epi_params['αᵍ'][i]
        hosp_rates[i] = (epi_params['μᵍ'][i] * (1 - epi_params['θᵍ'][i]) ) * epi_params['γᵍ'][i]

    # Computing daily new assymptomatic
    # alphas_vec = np.array([alphas[g] for g in sim_xa.coords['G'].values])
    sim_observables_xa.loc['A', :, :, :] = np.multiply(sim_observables_xa.loc['A', :, :, :], alphas)

    # hosp_rates_vec = np.array([hosp_rates[g] for g in sim_xa.coords['G'].values]) 
    sim_observables_xa.loc['I', :, :, :] = np.multiply(sim_observables_xa.loc['I', :, :, :], hosp_rates)

    dims = sim_observables_xa.dims
    data = sim_observables_xa.values
    coords = sim_observables_xa.coords

    coords['epi_states'] = ['I', 'H', 'D']
    sim_observables_xa = xr.DataArray(data, coords=coords, dims=dims)
    sim_observables_xa = sim_observables_xa.transpose('epi_states', 'G', 'M', 'T')
    
    sim_observables_xa.loc['D',:] = np.diff(sim_observables_xa.loc['D',:], prepend =0)
    
    return sim_observables_xa

  



