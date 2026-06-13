import pandas as pd
import requests
from shapely.geometry import shape, Point
import os

os.makedirs('./data/spatial/', exist_ok=True)

print("1. Fetching official Kerala boundary from OpenStreetMap...")
url = "https://nominatim.openstreetmap.org/lookup?osm_ids=R2018151&polygon_geojson=1&format=json"
headers = {'User-Agent': 'NITK_Hydrology_Research/GEE_Matched'}

response = requests.get(url, headers=headers)
kerala_data = response.json()
kerala_polygon = shape(kerala_data[0]['geojson'])

print("2. Applying the 0.125-degree spatial buffer...")
# This safely buffers the state by ~13.9km to capture coastal/border catchments
kerala_catchment = kerala_polygon.buffer(0.125)

print("3. Evaluating Grid Points against buffered boundary...")
# Load the master IMD baseline coordinates you previously extracted
df_imd = pd.read_csv('./data/raw/imd/IMD_Unique_Coordinates.csv')

valid_points = []
station_counter = 1

for index, row in df_imd.iterrows():
    pt = Point(row['longitude'], row['latitude'])
    
    # Strictly map only points that fall inside the buffered boundary
    if kerala_catchment.contains(pt):
        valid_points.append({
            'Grid_Station': f'Grid point {station_counter}',
            'latitude': row['latitude'], 
            'longitude': row['longitude']
        })
        station_counter += 1

df_valid = pd.DataFrame(valid_points)
output_path = './data/spatial/GMC_Grid_Points.csv'
df_valid.to_csv(output_path, index=False)

print(f"\n🎉 SUCCESS! Identified exactly {len(df_valid)} valid target grid points.")
print(f"📁 Master Spatial Map saved to: {output_path}\n")

print("--- COPY THIS ARRAY INTO YOUR GOOGLE EARTH ENGINE SCRIPT ---")
print("var ptList = [")
for index, row in df_valid.iterrows():
    print(f"  [{row['longitude']}, {row['latitude']}],")
print("];")
print("----------------------------------------------------------")
