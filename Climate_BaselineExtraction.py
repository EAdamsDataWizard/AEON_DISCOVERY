import xarray as xr
import pandas as pd

# The confirmed OPeNDAP URL for the 1971-2000 LTM baseline
url = "http://psl.noaa.gov/thredds/dodsC/Datasets/noaaglobaltemp/air.mon.ltm.nc"

try:
    # Load the dataset directly via the OPeNDAP protocol
    ds_baseline = xr.open_dataset(url)
    
    # Optional: Verify the metadata confirms 1971-2000 range
    print(f"Loaded dataset description: {ds_baseline.climatology_bounds.attrs['long_name']}")
    print(f"Dataset shape: {ds_baseline['air'].shape}")
    
    # You are now ready to use ds_baseline['air'] to convert anomalies to absolute temperatures
    
except Exception as e:
    print(f"Error loading data via OPeNDAP: {e}")
    print("Please ensure your Python environment has 'xarray' and 'netCDF4' installed.")

ds_baseline = ds_baseline.drop_encoding()

for attr in ['_NCProperties', 'NAME', 'CLASS']:
    if attr in ds_baseline.attrs:
        del ds_baseline.attrs[attr]

ds_baseline.to_netcdf("climate_baseline_1971_2000.nc", engine="netcdf4") 
print("Baseline secured to local storage.")
