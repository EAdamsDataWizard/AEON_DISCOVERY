import pandas as pd
import reverse_geocoder as rg
import pycountry
from global_land_mask import globe
from math import radians, cos, sin, asin, sqrt

FILE_PATH = r'c:\projects\climatepulse\Master_5x5_Grid_Registry.csv'

# Predefined Major Lake Centers (5-Degree Grid Alignment)
# All entries here are treated as the unified 'Deep_Lake' type.
LAKE_REGISTRY = {
    (47.5, 272.5): "Lake Superior", 
    (47.5, 277.5): "Lake Huron",
    (42.5, 272.5): "Lake Michigan",
    (42.5, 282.5): "Lake Erie/Ontario",
    (42.5, 52.5): "Caspian Sea",
    (37.5, 52.5): "Caspian Sea (South)",
    (-2.5, 32.5): "Lake Victoria",
    (52.5, 107.5): "Lake Baikal"
}

def haversine(lat1, lon1, lat2, lon2):
    R = 3959
    dlat, dlon = radians(lat2 - lat1), radians(lon2 - lon1)
    a = sin(dlat/2)**2 + cos(radians(lat1)) * cos(radians(lat2)) * sin(dlon/2)**2
    return 2 * R * asin(sqrt(a))

def rebuild_registry_v8_8():
    print("🚀 REBUILDING REGISTRY v8.8 (UNIFIED DEEP LAKES)...")
    df = pd.read_csv(FILE_PATH)
    
    coords = [(r['Lat_Key'], r['Lon_Key'] - 360 if r['Lon_Key'] > 180 else r['Lon_Key']) 
              for _, r in df.iterrows()]
    
    geo_results = rg.search(coords)
    surface_types, labels, country_codes = [], [], []

    for i, res in enumerate(geo_results):
        lat_grid_key = df.iloc[i]['Lat_Key']
        lon_grid_key = df.iloc[i]['Lon_Key']
        lat_norm, lon_norm = coords[i]
        
        on_land = globe.is_land(lat_norm, lon_norm)
        dist = haversine(lat_norm, lon_norm, float(res['lat']), float(res['lon']))

        # --- PRIORITY 1: PREDEFINED LAKES (UNIFIED) ---
        if (lat_grid_key, lon_grid_key) in LAKE_REGISTRY:
            lake_name = LAKE_REGISTRY[(lat_grid_key, lon_grid_key)]
            surface_types.append("Deep_Lake")  # <-- UNIFIED TYPE
            labels.append(lake_name)           # <-- CLEAN NAME
            country_codes.append("LAKE")
            continue # Skip subsequent checks

        # --- PRIORITY 2: POLAR ---
        elif abs(lat_grid_key) >= 60:
            surface_types.append("Polar")
            labels.append("Antarctica" if lat_grid_key <= -60 else "Arctic_Region")
            country_codes.append("AQ" if lat_grid_key <= -60 else "AR")
            continue
        
        # --- PRIORITY 3: LAND ---
        elif on_land and dist < 160:
            try:
                country = pycountry.countries.get(alpha_2=res['cc'])
                surface_types.append("Land")
                labels.append(country.name)
                country_codes.append(country.alpha_2)
            except:
                surface_types.append("Land")
                labels.append("Unknown Land")
                country_codes.append(res['cc'])
            continue

        # --- PRIORITY 4: OCEAN ---
        else:
            surface_types.append("Coastal_Ocean" if dist < 150 else "Deep_Ocean")
            labels.append("Oceanic Shelf" if dist < 150 else "Open Ocean")
            country_codes.append("N/A")

    df['Surface_Type'], df['Primary_Label'], df['Country_Code'] = surface_types, labels, country_codes
    df.to_csv(FILE_PATH, index=False)
    
    print("\n✅ REBUILD v8.8 COMPLETE (LAKES CONSOLIDATED)")
    print(df['Surface_Type'].value_counts())

if __name__ == "__main__":
    rebuild_registry_v8_8()