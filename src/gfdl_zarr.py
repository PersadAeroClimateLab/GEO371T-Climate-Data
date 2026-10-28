import xarray as xr
from os import listdir
from os.path import isfile
import dask.distributed as daskd


GFDL_HIST_INPUT_DIR = "/projects/dgs/persad_research/CAREER_DOWNLOADS/netcdf/GFDL_ensemble_historical"
GFDL_SSP585_INPUT_DIR = "/projects/dgs/persad_research/CAREER_DOWNLOADS/netcdf/GFDL_ensemble_ssp585"
HEAD_DATA_DIR = "../data/zarr_stores/"

if __name__ == "__main__":
    cluster = daskd.LocalCluster(n_workers=30, threads_per_worker=1, memory_limit="10GB", dashboard_address=":8002")
    client = cluster.get_client()
    
    for input_dir, label in [(GFDL_HIST_INPUT_DIR, "historical"), (GFDL_SSP585_INPUT_DIR, "ssp585")]:
        out_path = f"{HEAD_DATA_DIR}/gfdl-le_{label}_metrics_daily.zarr"
        
        members = listdir(input_dir)
        datasets = []
        for member in members:
            ds = xr.open_mfdataset(f"{input_dir}/{member}/*.nc", chunks={"time":360}, data_vars='all')
            pr_metrics = xr.Dataset(
                data_vars=dict(
                    one_day_pr=ds["pr"]*86400,
                    three_day_pr=ds["pr"].rolling(time=3, center=False).compute()*86400,
                    five_day_pr=ds["pr"].rolling(time=5, center=False).compute()*86400
                )
            )
            pr_metrics["one_day_pr"].attrs["units"] = "mm/day"
            pr_metrics["three_day_pr"].attrs["cell_methods"] = "area: time: mean (interval: 1 day); time: sum (interval: 1 day)"
            
            pr_metrics["three_day_pr"].attrs["units"] = "mm/3day"
            pr_metrics["three_day_pr"].attrs["long_name"] = "Rolling three-day sum of daily precipitation"
            pr_metrics["three_day_pr"].attrs["cell_methods"] = "area: time: mean (interval: 1 day); time: sum (interval: 3 day)"
            
            pr_metrics["five_day_pr"].attrs["units"] = "mm/5day"
            pr_metrics["five_day_pr"].attrs["long_name"] = "Rolling five-day sum of daily precipitation"
            pr_metrics["five_day_pr"].attrs["cell_methods"] = "area: time: mean (interval: 1 day); time: sum (interval: 5 day)"
            
            pr_metrics["lat"].attrs = ds["lat"].attrs
            pr_metrics["lon"].attrs = ds["lon"].attrs
            datasets.append(pr_metrics)
            del ds
        xr.concat(datasets, dim="member").assign_coords(dict(member=members)).to_zarr(out_path, zarr_format=2)