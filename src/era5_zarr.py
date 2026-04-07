import cdsapi
import xarray as xr
from os.path import isfile

HEAD_ERA5_DIR = "/local1/tmp/ERA5"
HEAD_DATA_DIR = "../data/"


def generate_era5_store(out_path_zarr):
    HEAD_ERA5_DIR = "/local1/tmp/ERA5"
    
    decoder = xr.coding.times.CFDatetimeCoder(use_cftime=True)
    ds = xr.open_mfdataset(f"{HEAD_ERA5_DIR}/*.nc", decode_times=decoder).rename({
        "valid_time": "time",
        "latitude": "lat",
        "longitude": "lon"
    }).chunk(time=-1, lat=103, lon=72)
    
    pr_metrics = xr.Dataset(
        data_vars=dict(
            one_day_pr=ds["tp"]*1000,
            three_day_pr=ds["tp"].rolling(time=3, center=False).sum()*1000,
            five_day_pr=ds["tp"].rolling(time=5, center=False).sum()*1000
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
    pr_metrics.to_zarr(out_path_zarr, zarr_format=2)


if __name__ == "__main__":
    client = cdsapi.Client(wait_until_complete=False)
    requests = []
    
    for year in range(1980, 2025):
        if isfile(f"{HEAD_ERA5_DIR}/ERA5_{year}_tp.nc"):
            continue
        dataset = "derived-era5-single-levels-daily-statistics"
        request = {
            "product_type": "reanalysis",
            "variable": ["total_precipitation"],
            "year": str(year),
            "month": [
                "01", "02", "03",
                "04", "05", "06",
                "07", "08", "09",
                "10", "11", "12"
            ],
            "day": [
                "01", "02", "03",
                "04", "05", "06",
                "07", "08", "09",
                "10", "11", "12",
                "13", "14", "15",
                "16", "17", "18",
                "19", "20", "21",
                "22", "23", "24",
                "25", "26", "27",
                "28", "29", "30",
                "31"
            ],
            "daily_statistic": "daily_sum",
            "time_zone": "utc+00:00",
            "frequency": "1_hourly"
        }
        requests.append((year, client.retrieve(dataset, request)))
    
    for year, req in requests:
        req.download(f"{HEAD_ERA5_DIR}/ERA5_{year}_tp.nc

    generate_era5_store("../data/zarr_stores/obs_era5_metrics_daily.zarr")