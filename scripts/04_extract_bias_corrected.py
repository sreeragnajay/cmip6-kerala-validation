import pandas as pd
import numpy as np
from scipy.spatial import cKDTree
import os

# --- Configuration ---
BASE_DIR = os.path.expanduser('~/Downloads/West_Coast')
MONTHLY_OUT = './data/processed/Monthly_RainGauge/'
GRID_MAP = './data/spatial/GMC_Grid_Points.csv'

grid_df = pd.read_csv(GRID_MAP)
target_coords = grid_df[['latitude', 'longitude']].values
station_names = grid_df['Grid_Station'].tolist()

models = [
    'ACCESS-CM2', 'ACCESS-ESM1-5', 'BCC-CSM2-MR', 'CanESM5', 
    'EC-Earth3', 'EC-Earth3-Veg', 'INM-CM4-8', 'INM-CM5-0', 
    'MPI-ESM1-2-HR', 'MPI-ESM1-2-LR', 'MRI-ESM2-0', 'NorESM2-LM', 'NorESM2-MM'
]

def extract_txt_matrix(file_path):
    with open(file_path, 'r') as f:
        lons = [float(x) if x != 'NaN' else np.nan for x in f.readline().strip().split()]
        lats = [float(x) if x != 'NaN' else np.nan for x in f.readline().strip().split()]

    valid_pts, col_indices = [], []
    for i, (lon, lat) in enumerate(zip(lons, lats)):
        if not np.isnan(lon) and not np.isnan(lat):
            valid_pts.append([lat, lon])
            col_indices.append(i)

    distances, indices = cKDTree(np.array(valid_pts)).query(target_coords)
    df_raw = pd.read_csv(file_path, sep=r'\s+', skiprows=2, header=None)
    
    df = pd.DataFrame()
    df['Date'] = pd.to_datetime(df_raw[0].astype(str) + '-' + df_raw[1].astype(str) + '-' + df_raw[2].astype(str))
    
    for station, idx in zip(station_names, indices):
        df[station] = df_raw[col_indices[idx]]
        
    return df.set_index('Date')

print("🚀 Starting Bias-Corrected Matrix Extraction...")

for model in models:
    print(f"   🔄 Extracting: {model}")
    hist_path = os.path.join(BASE_DIR, model, 'historical', 'PrecipData')
    fut_path = os.path.join(BASE_DIR, model, 'ssp585', 'PrecipData')
    
    try:
        df_hist = extract_txt_matrix(hist_path).loc['1990-01-01':'2014-12-31']
        df_fut = extract_txt_matrix(fut_path).loc['2015-01-01':'2025-12-31']
        
        # Merge, Resample to Monthly, Format to YYYY-MM
        df_seamless = pd.concat([df_hist, df_fut]).resample('MS').sum()
        df_seamless.index = df_seamless.index.strftime('%Y-%m')
        
        df_seamless.round(2).to_csv(os.path.join(MONTHLY_OUT, f"{model}_BiasCorrected_1990_2025.csv"))
    except Exception as e:
        print(f"      ❌ Failed: {e}")

print("✅ Phase 4 Complete: Bias-Corrected data extracted and integrated!")
