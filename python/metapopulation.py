import pandas as pd
import xarray as xr


class Metapopulation:
    def __init__(self, metapop_csv, rosetta_csv=None):
        self._metapop_csv = metapop_csv
        self._rosetta_csv = rosetta_csv
        self._region_ids = []
        self._region_areas = {}
        self._agent_types = []
        self._levels = []

        self._metapop_csv = metapop_csv
        pop_df = pd.read_csv(self._metapop_csv, index_col="id")
        
        self._region_ids   = pop_df.index.tolist()
        self._region_areas = pop_df['area'].to_dict()
        
        # Drop column with region areas
        pop_df = pop_df.drop('area', axis=1)
        
        if pop_df.shape[1] > 1:
            pop_df = pop_df.drop('total', axis=1)
        
        self._agent_types = pop_df.columns.tolist()
        self._populations = pop_df

        if self._rosetta_csv is not None:
            self._rosetta = pd.read_csv(self._rosetta_csv, dtype=object)
            self._levels = self._rosetta.columns
            self._rosetta = self._rosetta.set_index("level_1")
            
            assert set(self._rosetta.index) == set(self._region_ids)


    def as_datarray(self):
        da =  xr.DataArray(
                data=self._populations.values, name="population",
                coords={ "M": self._region_ids, "G": self._agent_types }, 
                dims=["M", "G"]
            )
        return da
    
    def aggregate_to_level(self, level, as_array=True): 
        if level == "level_1":
            df = self._populations
        else:
            df = pd.merge(self._populations, self._rosetta[[level]], left_index=True, right_index=True)
            df = df.groupby(level).sum()
        if as_array:
            da = xr.DataArray(
                    data=df.values, name="population",
                    coords={ "M": df.index.tolist(), "G": self._agent_types }, 
                    dims=["M", "G"]
                )
            return da

        return df
