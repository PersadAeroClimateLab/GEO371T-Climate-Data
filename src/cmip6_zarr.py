import s3fs
import xarray as xr
import numpy as np
import xesmf as xe
import pandas as pd
import dask.distributed as daskd
import cftime


HEAD_DATA_DIR = "../data/zarr_stores"


if __name__ == "__main__":
    cluster = daskd.LocalCluster(n_workers=40, threads_per_worker=1, memory_limit="4GB", dashboard_address=":8002")
    client = cluster.get_client()
    
    df = pd.read_csv("https://cmip6-pds.s3.amazonaws.com/pangeo-cmip6.csv")
    
    cmip_df = df[df["activity_id"] == "ScenarioMIP"]
    cmip_df = cmip_df[cmip_df["variable_id"] == "pr"]
    cmip_df = cmip_df[cmip_df["table_id"] == "day"]
    cmip_df = cmip_df[cmip_df["member_id"] == "r1i1p1f1"]
    ssp370_df = cmip_df[cmip_df["experiment_id"] == "ssp370"]
    ssp245_df = cmip_df[cmip_df["experiment_id"] == "ssp245"]
    ssp585_df = cmip_df[cmip_df["experiment_id"] == "ssp585"]
    
    cmip_df = df[df["activity_id"] == "CMIP"]
    cmip_df = cmip_df[cmip_df["variable_id"] == "pr"]
    cmip_df = cmip_df[cmip_df["table_id"] == "day"]
    cmip_df = cmip_df[cmip_df["member_id"] == "r1i1p1f1"]
    hist_df = cmip_df[cmip_df["experiment_id"] == "historical"]
    
    ssp245_models = ssp245_df["source_id"].unique()
    ssp585_models = ssp585_df["source_id"].unique()
    hist_models = hist_df["source_id"].unique()
    common_models = []
    for model in ssp370_df["source_id"].unique():
        if model in ssp245_models and model in ssp585_models and model in hist_models:
            common_models.append(model)
    
    ssp370_df = ssp370_df[ssp370_df['source_id'].isin(common_models)]
    ssp245_df = ssp245_df[ssp245_df['source_id'].isin(common_models)]
    ssp585_df = ssp585_df[ssp585_df['source_id'].isin(common_models)]
    hist_df = hist_df[hist_df['source_id'].isin(common_models)]
    
    cmip_stores = pd.concat([ssp370_df, ssp245_df, ssp585_df, hist_df]).sort_values(by="source_id")
    
    fs = s3fs.S3FileSystem(anon=True)
    datasets = {}
    
    for index in range(cmip_stores.shape[0]):
        print(index, end=" ")
        model = cmip_stores.iloc[index]["source_id"]
        experiment = cmip_stores.iloc[index]["experiment_id"]
        mapper = fs.get_mapper(cmip_stores.iloc[index]["zstore"])
        
        ds = xr.open_zarr(mapper, consolidated=True)
        
        lat = np.arange(-89.25, 90, 1.5) # 120 points
        lon = np.arange(0, 360, 2.5) # 144 points
        
        grid_out = xr.Dataset({
            'lat': (['lat'], lat),
            'lon': (['lon'], lon),
        })
        
        regridder = xe.Regridder(ds, grid_out, 'conservative')
        
        ds_regridded = regridder(ds, keep_attrs=True)
        ds_regrid_scaled = ds_regridded*86400
        
        pr_metrics = xr.Dataset(
            data_vars=dict(
                one_day_pr=ds_regrid_scaled["pr"],
                three_day_pr=ds_regrid_scaled["pr"].rolling(time=3, center=False).sum(),
                five_day_pr=ds_regrid_scaled["pr"].rolling(time=5, center=False).sum()
            )
        )
        pr_metrics["one_day_pr"].attrs["units"] = "mm/day"
        pr_metrics["three_day_pr"].attrs["cell_methods"] = "area: time: mean (interval: 1 day); time: sum (interval: 1 day); time: max (interval: 1 year)"
        
        pr_metrics["three_day_pr"].attrs["units"] = "mm/3day"
        pr_metrics["three_day_pr"].attrs["long_name"] = "Rolling three-day sum of daily precipitation"
        pr_metrics["three_day_pr"].attrs["cell_methods"] = "area: time: mean (interval: 1 day); time: sum (interval: 3 day); time: max (interval: 1 year)"
        
        pr_metrics["five_day_pr"].attrs["units"] = "mm/5day"
        pr_metrics["five_day_pr"].attrs["long_name"] = "Rolling five-day sum of daily precipitation"
        pr_metrics["five_day_pr"].attrs["cell_methods"] = "area: time: mean (interval: 1 day); time: sum (interval: 5 day); time: max (interval: 1 year)"
        
        pr_metrics["lat"].attrs = ds["lat"].attrs
        pr_metrics["lon"].attrs = ds["lon"].attrs
    
        datasets[f"{model}:{experiment}"] = pr_metrics
    
    
    da_lists = {scenario: [] for scenario in ["historical", "ssp370", "ssp245", "ssp585"]}
    model_labels = {scenario: [] for scenario in ["historical", "ssp370", "ssp245", "ssp585"]}
    
    for entry in datasets:
        model, scenario = entry.split(":")
    
        if model == "KACE-1-0-G" or model == "ACCESS-CM2" or model == "IITM-ESM":
            continue
        
        if scenario == "historical":
            ds = datasets[entry].sel(time=slice("1920-01-01", "2014-12-30")).convert_calendar("noleap", use_cftime=True, align_on="year")
            ds = ds.assign_coords(time=xr.date_range("1920-01-01", "2014-12-30", calendar="noleap", freq="D", use_cftime=True))
        else:
            ds = datasets[entry].sel(time=slice("2015-01-01", "2099-12-30")).convert_calendar("noleap", use_cftime=True, align_on="year")
            ds = ds.assign_coords(time=xr.date_range("2015-01-01", "2099-12-30", calendar="noleap", freq="D", use_cftime=True))
        if ds.time.size == 0:
            continue
        model_labels[scenario].append(model)
        da_lists[scenario].append(ds)

    xr.concat(da_lists["historical"], dim="model").assign_coords(dict(model=model_labels["historical"])).chunk(time=-1, lat=30, lon=72).to_zarr(f"{HEAD_DATA_DIR}/cmip6_historical_metrics_daily.zarr", zarr_format=2)
    xr.concat(da_lists["ssp370"], dim="model").assign_coords(dict(model=model_labels["ssp370"])).chunk(time=-1, lat=30, lon=72).to_zarr(f"{HEAD_DATA_DIR}/cmip6_ssp370_metrics_daily.zarr", zarr_format=2)
    xr.concat(da_lists["ssp245"], dim="model").assign_coords(dict(model=model_labels["ssp245"])).chunk(time=-1, lat=30, lon=72).to_zarr(f"{HEAD_DATA_DIR}/cmip6_ssp245_metrics_daily.zarr", zarr_format=2)
    xr.concat(da_lists["ssp585"], dim="model").assign_coords(dict(model=model_labels["ssp585"])).chunk(time=-1, lat=30, lon=72).to_zarr(f"{HEAD_DATA_DIR}/cmip6_ssp585_metrics_daily.zarr", zarr_format=2)