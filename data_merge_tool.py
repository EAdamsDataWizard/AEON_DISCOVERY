import duckdb
import pandas as pd

# Configuration
REGISTRY = r'c:\projects\climatepulse\Master_5x5_Grid_Registry.csv'
ANCIENT = r'c:\projects\climatepulse\Ancient_Data_Normalized.csv'
MODERN = r'c:\projects\climatepulse\Modern_Data_Normalized.csv'
FINAL_PARQUET = r'c:\projects\climatepulse\Master_Climate_Data.parquet'

con = duckdb.connect(':memory:')

print("🧵 STITCHING MASTER CLIMATE DATA (v8.0)...")

# 1. Load the three components
con.execute(f"CREATE VIEW registry AS SELECT * FROM read_csv_auto('{REGISTRY}')")
con.execute(f"CREATE VIEW ancient AS SELECT * FROM read_csv_auto('{ANCIENT}')")
con.execute(f"CREATE VIEW modern AS SELECT * FROM read_csv_auto('{MODERN}')")

# 2. DELTA CALCULATION REMOVED (V8.0 - Data Transparency)
print("🧮 Bypassing Delta Offset calculation...")
delta = 0.0 # Hardcoded to zero for raw data merge
print(f"📏 Using Offset: {delta:.4f} °F")

# 3. COMBINE DATASETS WITHOUT OFFSET AND WITH SURFACE TYPES
con.execute(f"""
    CREATE OR REPLACE TABLE master_final AS
    SELECT 
        a.Date, r.Primary_Label, r.Surface_Type, 
        a.Temp_F AS Temp_F,  -- Offset removed for V8.0
        a.Uncert_C, 'Ancient' AS Source
    FROM ancient a
    JOIN registry r ON a.Lat_Key = r.Lat_Key AND a.Lon_Key = r.Lon_Key
    
    UNION ALL
    
    SELECT 
        m.Date, r.Primary_Label, r.Surface_Type, 
        m.Temp_F, m.Uncert_C, 'Modern' AS Source
    FROM modern m
    JOIN registry r ON m.Lat_Key = r.Lat_Key AND m.Lon_Key = r.Lon_Key
""")

# 4. EXPORT TO PARQUET
print(f"💾 Exporting to: {FINAL_PARQUET}")
con.execute(f"COPY master_final TO '{FINAL_PARQUET}' (FORMAT PARQUET)")

print("✅ SUCCESS. Master Brain v8.0 (Raw Data) is stitched and ready for Power BI.")
con.close()