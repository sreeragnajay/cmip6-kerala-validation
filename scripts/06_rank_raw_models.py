import os
import glob
import pandas as pd

# Matched exactly to your folder names
stats_dir = './data/processed/Statistics/'  
output_summary_path = './data/processed/summary/raw_models_ranked_summary.csv'

def generate_model_rankings():
    # Find all CSV files in the raw stats directory
    csv_files = glob.glob(os.path.join(stats_dir, '*.csv'))
    
    if not csv_files:
        print(f"❌ No CSV files found in {stats_dir}. Please check your path!")
        return

    summary_data = []

    for file_path in csv_files:
        filename = os.path.basename(file_path)
        
        # SKIP the grid point map or any helper files that aren't model stats
        if "Grid_Point" in filename or "Map" in filename:
            continue
            
        # Cleanly extract model name (e.g., 'ACCESS-CM2_Raw_GCM_Monthly_Stats.csv' -> 'ACCESS-CM2')
        model_name = filename.split('_')[0] 
        
        try:
            df = pd.read_csv(file_path)
            
            # Verify required columns exist or handle variations
            corr_col = 'Correlation' if 'Correlation' in df.columns else None
            rmse_col = 'RMSE' if 'RMSE' in df.columns else None
            
            # Handle 'PBIAS' vs 'PBIAS (%)' dynamic header naming
            pbias_col = None
            for col in ['PBIAS (%)', 'PBIAS']:
                if col in df.columns:
                    pbias_col = col
                    break
            
            if not corr_col or not rmse_col or not pbias_col:
                print(f"⚠️ Skipping {filename}: Missing columns. Found headers: {list(df.columns)}")
                continue
                
            # Calculate metrics across all 77 grid points safely
            mean_corr = df[corr_col].mean()
            median_corr = df[corr_col].median()
            mean_rmse = df[rmse_col].mean()
            mean_abs_pbias = df[pbias_col].abs().mean() 
            
            summary_data.append({
                'Model Name': model_name,
                'Mean Correlation': round(mean_corr, 4),
                'Median Correlation': round(median_corr, 4),
                'Mean RMSE': round(mean_rmse, 2),
                'Mean Abs PBIAS (%)': round(mean_abs_pbias, 2)
            })
            
        except Exception as e:
            print(f"⚠️ Error processing file {filename}: {e}")

    if not summary_data:
        print("❌ Error: No valid model data could be parsed. Check column names!")
        return

    # Create summary DataFrame
    summary_df = pd.DataFrame(summary_data)
    
    # Rank models: Highest Raw Correlation wins!
    summary_df = summary_df.sort_values(by='Mean Correlation', ascending=False).reset_index(drop=True)
    
    # Save the ranked summary matrix
    os.makedirs(os.path.dirname(output_summary_path), exist_ok=True)
    summary_df.to_csv(output_summary_path, index=False)
    
    print("\n📊 ==== RAW GCM PERFORMANCE SUMMARY ====")
    print(summary_df.to_string(index=True))
    print(f"\n💾 Summary report successfully saved to: {output_summary_path}")

if __name__ == '__main__':
    generate_model_rankings()