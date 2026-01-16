import pandas as pd
import numpy 

file_path = 'GlobalLandTemperaturesByCity.csv'

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

#opens first 100 rows and convert DateTime object to dt64 format
df = pd.read_csv(file_path)
df['dt'] = pd.to_datetime(df['dt'])

tracker.log_event(df,"Initial Load")

#converts float64 to float32
def conv_floats(data):
    fcol = data.select_dtypes(include=['float64']).columns
    for col in fcol:
        data[col] = pd.to_numeric(data[col], downcast='float')

tracker.log_event(df, "Float Conversion", action_func=conv_floats)

#Transforms string coordinates like '57.05N' to numeric float 57.05. 
#Handles hemisphere logic: S and W become negative.
def conv_coords(data):
    """
    """
    for col in ['Latitude', 'Longitude']:
        mask = data[col].str.contains('S|W', na=False)
        data[col] = data[col].str.replace(r'[^0-9.]', '', regex=True).astype(float)
        #Apply negative sign to South and West
        data.loc[mask, col] *= -1
        data[col] = pd.to_numeric(data[col], downcast='float')
tracker.log_event(df,"Coordinate Conversion",action_func=conv_coords)

#Converts object columns (City, Country) to Categorical.
def conv_categories(data):
    """
    """
    # Identify remaining object columns (usually City and Country)
    obj_cols = data.select_dtypes(include=['object']).columns
    
    for col in obj_cols:
        # Only convert if there are repeating values (efficiency check)
        if data[col].nunique() < len(data[col]):
            data[col] = data[col].astype('category')
tracker.log_event(df,"Category Conversion", action_func=conv_categories)


########################################################################
early_window = df[df['dt'] <= '1752-09-01']

# 2. List every unique city found in this time block
# .unique() includes all cities found, even if their temp is NaN
all_cities_present = early_window['City'].unique()

print(f"--- Cities Found in 1743-1752 Window ---")
print(all_cities_present)
print(f"Total Unique Cities: {len(all_cities_present)}")


tracker.show_report()
#exit()

print("---Data Headers & Types---")
print(df.info())
print("\n---First 5 rows---")
print(df.head())
print("\n---Last 5 rows---")
print(df.tail())

total_nulls = df[df['AverageTemperature'].isna()]

# Show which countries have nulls at the END of the timeline
print("\n--- Modern Era Nulls (Post-2010) ---")
print(total_nulls[total_nulls['dt'] > '2010-01-01'])

# Get a final count for every country
print("\n--- Null Count by Country ---")
print(total_nulls.groupby('Country').size())

output_path = "ancient_data_optimized.csv"
df.to_csv(output_path, index=False)

print("\n" + "="*50)
print(f"✅ Data fully optimized and exported to:\n{output_path}")
print(f"Total Rows for Power BI: {len(df)}")
print("="*50)

###Grabs null data for data audit
###null AUDITING
#missing_data = df[df['AverageTemperature'].isna()]
#print("\n--- Rows with Missing Temperature ---")
#print(missing_data[['dt', 'AverageTemperature']])
#print(f"\nTotal rows with missing data: {len(missing_data)}")

#missing_data_uncert = df[df['AverageTemperatureUncertainty'].isna()]
#print("\n--- Rows with Missing Temperature Uncertainty---")
#print(missing_data[['dt', 'AverageTemperatureUncertainty']])
#print(f"\nTotal rows with missing data: {len(missing_data_uncert)}")
#null_audit_df = df[df['AverageTemperature'].isna() | df['AverageTemperatureUncertainty'].isna()].copy()
# --- 2. EXPORT FOR POWER BI ---
# We keep the converted dt and location data so you can map the gaps
#null_audit_df.to_csv("climate_pulse_null_audit.csv", index=False)
#print(f"\n--- Audit Ready ---")
#print(f"Exported {len(null_audit_df)} null rows to 'climate_pulse_null_audit.csv'")
#print("Analyze this in Power BI to see the geographic/temporal clusters.")