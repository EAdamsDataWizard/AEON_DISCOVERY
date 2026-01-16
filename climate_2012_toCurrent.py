import xarray as xr
import pandas as pd
import os

#Creates a report that tracks memory savings through downcasting
class MemoryTracker:
    def __init__(self):
        self.history = []

    def log_event(self, df, event_name, action_func=None):
        """
        """
        # 1. Measure BEFORE
        before_mem = df.memory_usage(deep=True).sum() / 1024**2
        
        # 2. Perform the ACTION (if one is provided)
        if action_func:
            action_func(df)
        
        # 3. Measure AFTER
        after_mem = df.memory_usage(deep=True).sum() / 1024**2
        
        # 4. Calculate SAVINGS
        savings_pct = ((before_mem - after_mem) / before_mem) * 100 if before_mem > 0 else 0
        
        # 5. Store the brick
        self.history.append({
            "Event": event_name,
            "Before (MB)": round(before_mem, 4),
            "After (MB)": round(after_mem, 4),
            "Savings (%)": round(savings_pct, 2)
        })

    def show_report(self):
        """Prints the final summary table."""
        report_df = pd.DataFrame(self.history)
        print("\n" + "="*50)
        print("      COMPRESSION ANALYSIS REPORT")
        print("="*50)
        print(report_df.to_string(index=False))
        print("="*50)

#Function used to call the memory report - tracker.show_report()
tracker = MemoryTracker()

def optimize_memory(df):
    # Downcast Floats (64-bit to 32-bit is safe for climate decimals)
    float_cols = [c for c in df.columns if df[c].dtype == 'float64']
    for col in float_cols:
        df[col] = pd.to_numeric(df[col], downcast='float')

    # Downcast Integers (Month)
    if 'Month' in df.columns:
        df['Month'] = pd.to_numeric(df['Month'], downcast='integer')

    return df

modern_file = r'c:\projects\climatepulse\NOAAGlobalTemp_v6.0.0_gridded_s185001_e202511_c20251207T151328.nc'
baseline_file = r'c:\projects\climatepulse\climate_baseline_1971_2000.nc'

# --- SECTION 1: MODERN DATA ---
print("Opening Modern Data...")
ds_modern = xr.open_dataset(modern_file)
df_modern = (
    ds_modern.sel(time=slice('1850-01-01', '2025-11-01'))
    .squeeze('z')['anom']
    .to_dataframe()
    .reset_index()
)

df_modern = df_modern.drop(columns=['z']).rename(columns={
    'time': 'Date', 'lat': 'Latitude', 'lon': 'Longitude', 'anom': 'Temp_Anom_C'
})
df_modern['Month'] = df_modern['Date'].dt.month

# --- SECTION 2: BASELINE DATA (FIXED FOR YEAR 0001) ---
print("\nLoading Climatology Baseline...")
ds_base = xr.open_dataset(baseline_file)

# FIX: Extract Month as an integer BEFORE it touches Pandas to avoid overflow
ds_base.coords['Month'] = ds_base['time.month']
df_base = ds_base['air'].to_dataframe().reset_index()

# Clean up baseline: Drop problematic 'time' and rename
df_base = df_base.drop(columns=['time']).rename(columns={
    'air': 'Baseline_C', 'lat': 'Latitude', 'lon': 'Longitude'
})
df_base = df_base[['Month', 'Latitude', 'Longitude', 'Baseline_C']]

# --- SECTION 3: MERGE & CALCULATE ---
print("Merging datasets. This can take a few minutes for 5.4M rows...")
df_final = pd.merge(df_modern, df_base, on=['Month', 'Latitude', 'Longitude'], how='left')

print("Converting Temperature Data to F...")
# Absolute Celsius = Anomaly + Baseline
df_final['Temp_Abs_C'] = df_final['Temp_Anom_C'] + df_final['Baseline_C']

# FIX: Use Absolute Celsius for the Fahrenheit conversion
df_final['Temp_in_F'] = (df_final['Temp_Abs_C'] * 1.8) + 32

print("\n--- Calculations Complete! ---")
cols = ['Date', 'Latitude', 'Longitude', 'Temp_Anom_C', 'Temp_in_F']
print(df_final[cols].head(3))
print(df_final[cols].tail(3))

tracker.log_event(
    df_final, 
    "Downcasting 1850-2025 Data", 
    action_func=lambda d: optimize_memory(d)
)

# 3. Show the final audit report
tracker.show_report()

output_path = r'c:\projects\climatepulse\modern_climate_optimized.csv'
df_final.to_csv(output_path, index=False)

print(f"🚀 Modern branch SECURED: {output_path}")