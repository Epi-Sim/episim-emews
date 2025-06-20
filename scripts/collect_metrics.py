import os, sys
import json
import glob
import pandas as pd

base_folder = os.path.realpath(os.path.join(os.path.dirname(sys.argv[0]), ".."))
custom_module_path = os.path.join(base_folder, "python")
sys.path.append(custom_module_path)

import episim_evaluate

def collect_results(experiment_folder):
    
    data_folder = os.path.join(experiment_folder, "data")
    pattern = os.path.join(experiment_folder, "instance_*")
    workflow_json   = os.path.join(data_folder, "workflow_settings_fit.json")

    data_rows = []
    #ANALYZE THE FULL EXPERIMENT LOOKING FOR THE BEST SIMULATION (min RMSE)
    for instance_path in glob.glob(pattern):

        path_pieces    = instance_path.split("/")
        instance_id    = path_pieces[-1]
        
        split_instance = instance_id.split("_")
        if len(split_instance) == 2:
            gen = 1
            ind = split_instance[1]
        elif len(split_instance) == 3:
            gen = split_instance[1]
            ind = split_instance[2]
        else:
            raise Exception(f"Invalid directory name for instance {instance_id}")

        config_json   = os.path.join(instance_path, "config.json")
        with open(config_json, 'r') as f:
            config = json.load(f)

        epi_params = config.get("epidemic_params", {})
        npi_params = config.get("NPI", {})
        pop_params = config.get("population_params", {})

        G_labels = pop_params.get("G_labels", [])

        # Flatten both dictionaries and combine them
        flat_row = {}
        flat_row["instance_path"] = instance_path
        flat_row["gen"] = gen
        flat_row["ind"] = ind

        for key, value in epi_params.items():
            if isinstance(value, list) and len(value) == len(G_labels):
                for label, v in zip(G_labels, value):
                    flat_row[f"{key}{label}"] = v
            else:
                flat_row[key] = value

        for key, value in npi_params.items():
            if isinstance(value, list):
                for i, v in enumerate(value):
                    flat_row[f"{key}_{i}"] = v
            else:
                flat_row[key] = value    

        cost = episim_evaluate.evaluate_obj(instance_path, data_folder, workflow_json)
        flat_row["cost"] = cost
        data_rows.append(flat_row)

    # Create a DataFrame from the list of dictionaries
    df = pd.DataFrame(data_rows)

    # Remove columns with only one unique value
    df = df.loc[:, df.nunique() != 1]

    # Sort the DataFrame by 'cost' in ascending order
    df = df.sort_values(by=["cost"])

    return df


if __name__ == "__main__":

    experiment_folder = sys.argv[1]
    print(f"- Collecting metrics from experiment {experiment_folder}")
    df = collect_results(experiment_folder)

    # Save the DataFrame to a txt file
    output_name = os.path.join(experiment_folder, "experiment_results.csv")

    print(f"- Writing experiment metrics into {output_name}")
    df.to_csv(output_name, index=False, encoding='utf-8')
