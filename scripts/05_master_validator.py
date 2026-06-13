import pandas as pd
import numpy as np
import os
import glob
from scipy.stats import pearsonr

# --- Configuration ---
MONTHLY_DIR = './data/processed/Monthly_RainGauge/'
STATS_OUT = './data/processed/Statistics/'
# Make sure your IMD file is named exactly this after running Script 3
IMD_FILE = os.path.join(MONTHLY_DIR, 'IMD_Kerala_1990_to_2025_Combined.csv')

os.makedirs(STATS_OUT, exist_ok=True)

print("📊 Loading Master IMD Baseline...")
imd_df = pd.read_csv(IMD_FILE, index_col='Date').loc['1990-01':'2014-11']

gcm_files = [f for f in glob.glob(os.path.join(MONTHLY_DIR, '*.csv')) if 'IMD' not in f]

print(f"🚀 Found {len(gcm_files)} models for validation. Crunching statistics...")

for file in gcm_files:
    filename = os.path.basename(file)
    model_name = filename.replace('.csv', '')
    print(f"   🔄 Evaluating: {model_name}")
    
    gcm_df = pd.read_csv(file, index_col='Date').loc['1990-01':'2014-11']
    model_stats = []
    
    for station in imd_df.columns:
        if station in gcm_df.columns:
            obs = imd_df[station].values
            sim = gcm_df[station].values
            
            # Correlation
            corr = 0 if np.std(obs) == 0 or np.std(sim) == 0 else pearsonr(obs, sim)[0]
            
            # RMSE (Converted from monthly sum back to daily average error)
            rmse_daily = np.sqrt(np.mean((sim - obs)**2)) / 30.4375 
            
            # PBIAS
            pbias = 0 if np.sum(obs) == 0 else 100 * np.sum(sim - obs) / np.sum(obs)
                
            model_stats.append({
                'Grid_Station': station,
                'Correlation': round(corr, 3),
                'RMSE (mm/day)': round(rmse_daily, 2),
                'PBIAS (%)': round(pbias, 1)
            })
            
    df_stats = pd.DataFrame(model_stats)
    df_stats.to_csv(os.path.join(STATS_OUT, f"{model_name}_Validation_Stats.csv"), index=False)

print("\n" + "="*55)
print("🏆 PIPELINE COMPLETE! ALL STATISTICS GENERATED SUCCESSFULLY.")
print("="*55)
