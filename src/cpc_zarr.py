import xarray as xr

HEAD_CPC_DIR = "/local1/tmp/CPC"
HEAD_DATA_DIR = "../data/"

if __name__ == "__main__":
    decoder = xr.coding.times.CFDatetimeCoder(use_cftime=True)
    ds = xr.open_mfdataset(f"{HEAD_CPC_DIR}/*.nc", decode_times=decoder).chunk(time=-1, lat=90, lon=90)
    
    pr_metrics = xr.Dataset(
        data_vars=dict(
            one_day_pr_max=ds["precip"].compute()*1000,
            three_day_pr_max=ds["precip"].rolling(time=3, center=False).sum().compute()*1000,
            five_day_pr_max=ds["precip"].rolling(time=5, center=False).sum().compute()*1000
        )
    )
    pr_metrics["one_day_pr_max"].attrs["units"] = "mm/day"
    pr_metrics["three_day_pr_max"].attrs["cell_methods"] = "area: time: mean (interval: 1 day); time: sum (interval: 1 day); time: max (interval: 1 year)"
    
    pr_metrics["three_day_pr_max"].attrs["units"] = "mm/3day"
    pr_metrics["three_day_pr_max"].attrs["long_name"] = "Rolling three-day sum of daily precipitation"
    pr_metrics["three_day_pr_max"].attrs["cell_methods"] = "area: time: mean (interval: 1 day); time: sum (interval: 3 day); time: max (interval: 1 year)"
    
    pr_metrics["five_day_pr_max"].attrs["units"] = "mm/5day"
    pr_metrics["five_day_pr_max"].attrs["long_name"] = "Rolling five-day sum of daily precipitation"
    pr_metrics["five_day_pr_max"].attrs["cell_methods"] = "area: time: mean (interval: 1 day); time: sum (interval: 5 day); time: max (interval: 1 year)"
    
    pr_metrics["lat"].attrs = ds["lat"].attrs
    pr_metrics["lon"].attrs = ds["lon"].attrs
    pr_metrics.to_netcdf("data/obs_CPC_yr_pr-metrics.nc")