import pandas as pd
import numpy as np

# Configuration
INPUT_FILE = r'c:\projects\climatepulse\ancient_data_optimized.csv'
OUTPUT_FILE = r'c:\projects\climatepulse\Ancient_Data_Normalized.csv'

def normalize_ancient():
    print("🔄 Normalizing Ancient Data (Scale: 0-360 | Precision: 5-Deg Snap)...")
    
    # Load the raw ancient data
    df = pd.read_csv(INPUT_FILE)

    df['dt'] = pd.to_datetime(df['dt'])
    
    # 1. Filter to Pre-1850 only (The "Ancient" period)
    df['dt'] = pd.to_datetime(df['dt'])
    df = df[df['dt'] < '1850-01-01'].copy()
    
    # 2. Convert Longitude to 0-360 Scale
    # Logic: If negative, add 360 (e.g., -0.1 becomes 359.9)
    df['Longitude_360'] = df['Longitude'].apply(lambda x: x + 360 if x < 0 else x)
    
    # 3. THE SNAP: Align to 5-Degree Grid Centers
    # Formula: (Floor to nearest 5) + 2.5
    # This forces 50.63 -> 52.5 and 6.34 -> 7.5
    df['Lat_Snap'] = (np.floor(df['Latitude'] / 5) * 5) + 2.5
    df['Lon_Snap'] = (np.floor(df['Longitude_360'] / 5) * 5) + 2.5
    
    # 4. Clean up Column names for the Master Join
    df_clean = df[['dt', 'Lat_Snap', 'Lon_Snap', 'AverageTemperature', 'AverageTemperatureUncertainty']].copy()
    df_clean.columns = ['Date', 'Lat_Key', 'Lon_Key', 'Temp_C', 'Uncert_C']
    
    # 5. Convert to Fahrenheit (Absolute)
    df_clean['Temp_F'] = (df_clean['Temp_C'] * 1.8) + 32
    
    # Save the normalized file
    df_clean.to_csv(OUTPUT_FILE, index=False)
    
    print(f"✅ Normalization Complete: {OUTPUT_FILE}")
    print(f"📊 Rows Processed: {len(df_clean)}")
    print(f"📍 Sample Snap: Original({df.iloc[0]['Latitude']}) -> Grid({df_clean.iloc[0]['Lat_Key']})")

if __name__ == "__main__":
    normalize_ancient()