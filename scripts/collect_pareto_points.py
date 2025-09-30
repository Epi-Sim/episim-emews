import pandas as pd
import os
import glob
import sys




def merge_csv (experiment_folder):

	pattern = os.path.join(experiment_folder, "instance_*", "output", "pareto_points.csv")

	dfs = []
	for path in glob.glob(pattern):
		df = pd.read_csv(path)
		dfs.append(df)
	
	merged_df = pd.concat(dfs, ignore_index=True)
	
	return merged_df


if __name__ == "__main__":
	
	experiment_folder = sys.argv[1]
	print(f"- Merging pareto points form {experiment_folder}")

	merged_df = merge_csv(experiment_folder)
	output_path = os.path.join(experiment_folder, "pareto_points.csv")
	merged_df.to_csv(output_path, index=False)
	print(f"- Merged pareto points saved to {output_path}")