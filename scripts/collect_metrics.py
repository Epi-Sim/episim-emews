import os, sys
import json
import glob
import pandas as pd



base_folder = os.path.realpath(os.path.join(os.path.dirname(sys.argv[0]), ".."))

sys.path.append(f"{base_folder}/python")

import episim_evaluate

experiment_folder = sys.argv[1]

data_folder = f"{experiment_folder}/data"
pattern = f"{experiment_folder}/instance_*"

workflow_json   = os.path.join(data_folder, "workflow_settings_fit.json")

#ANALYZE THE FULL EXPERIMENT LOOKING FOR THE BEST SIMULATION (min RMSE)

data_rows = []

for path in glob.glob(pattern):
    split_path = path.split("/")
    instance = split_path[-1]
    split_instance = instance.split("_")
    gen = split_instance[1]
    ind = split_instance[2]

    instance_folder = path

    config_json   = os.path.join(instance_folder, "config.json")
    with open(config_json, 'r') as f:
        config = json.load(f)

    epi_params = config.get("epidemic_params", {})
    npi_params = config.get("NPI", {})
    pop_params = config.get("population_params", {})

    G_labels = pop_params.get("G_labels", [])

    # Flatten both dictionaries and combine them
    flat_row = {}

    flat_row["gen"] = gen
    flat_row["ind"] = ind

    for key, value in epi_params.items():
        if isinstance(value, list) and len(value) == len(G_labels):
            for label, v in zip(G_labels, value):
                flat_row[f"{key}_{label}"] = v
        else:
            flat_row[key] = value

    for key, value in npi_params.items():
        if isinstance(value, list):
            for i, v in enumerate(value):
                flat_row[f"{key}_{i}"] = v
        else:
            flat_row[key] = value    


    cost = episim_evaluate.evaluate_obj(instance_folder, data_folder, workflow_json)

    flat_row["cost"] = cost

    data_rows.append(flat_row)

# Create a DataFrame from the list of dictionaries
df = pd.DataFrame(data_rows)

# Remove columns with only one unique value
df = df.loc[:, df.nunique() != 1]

# Sort the DataFrame by 'cost' in ascending order
df = df.sort_values(by=["cost"])

# Save the DataFrame to a txt file
output_name = os.path.join(experiment_folder, "experiment_results.txt")
df.to_csv(output_name, index=False)
print(f"Experiment results saved to {output_name}")

