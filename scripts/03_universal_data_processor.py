import pandas as pd
import os
import glob
from scipy.spatial import cKDTree

# --- Configuration ---
INPUT_DIR = './data/raw/' # Put raw IMD and raw NASA files here
DAILY_OUT = './data/processed/Daily_RainGauge/'
MONTHLY_OUT = './data/processed/Monthly_RainGauge/'
GRID_MAP = './data/spatial/GMC_Grid_Points.csv'

os.makedirs(DAILY_OUT, exist_ok=True)
os.makedirs(MONTHLY_OUT, exist_ok=True)

# Load target 77 points
grid_df = pd.read_csv(GRID_MAP)
target_coords = grid_df[['latitude', 'longitude']].values
station_names = grid_df['Grid_Station'].tolist()

# Find all CSVs
raw_files = glob.glob(os.path.join(INPUT_DIR, '**/*.csv'), recursive=True)

print(f"🚀 Found {len(raw_files)} raw files. Starting Universal Processor...")

for file in raw_files:
    filename = os.path.basename(file)
    print(f"   🔄 Processing: {filename}")
    
    # Load and standardize columns
    df = pd.read_csv(file)
    df.columns = df.columns.str.strip().str.lower()
    df.rename(columns={'time': 'date', 'rain': 'precipitation_mm_day', 'pr': 'precipitation_mm_day'}, inplace=True)
    
    # Clean Dates & Drop GEE Duplicates
    df['date'] = pd.to_datetime(df['date'].astype(str).str[:10], errors='coerce')
    df = df.dropna(subset=['date'])
    df = df.drop_duplicates(subset=['date', 'latitude', 'longitude'])
    
    # KD-Tree Spatial Snapping
    unique_coords = df[['latitude', 'longitude']].drop_duplicates()
    tree = cKDTree(unique_coords.values)
    distances, indices = tree.query(target_coords)
    
    matched_coords = unique_coords.iloc[indices].copy()
    matched_coords['Grid_Station'] = station_names
    
    # Merge and Pivot (Daily)
    df = pd.merge(df, matched_coords, on=['latitude', 'longitude'], how='inner')
    daily_pivot = df.pivot(index='date', columns='Grid_Station', values='precipitation_mm_day')
    daily_pivot.sort_index(inplace=True)
    daily_pivot.index.name = 'Date'
    
    # Save Daily
    daily_pivot.round(2).to_csv(os.path.join(DAILY_OUT, filename))
    
    # Resample and Save Monthly
    monthly_pivot = daily_pivot.resample('MS').sum()
    monthly_pivot.index = monthly_pivot.index.strftime('%Y-%m')
    monthly_pivot.round(2).to_csv(os.path.join(MONTHLY_OUT, filename))

print("✅ Phase 3 Complete: All data processed, pivoted, and aggregated to YYYY-MM!")
