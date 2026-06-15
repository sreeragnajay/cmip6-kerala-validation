import os
import glob
import pandas as pd

# Updated to match the exact folder structure in your screenshots
input_dir = './data/processed/Bias_Corrected_Data/GMC_Daily_RainGauge/'
output_file = './data/processed/summary/MME_BiasCorrected_Daily_TimeSeries.csv'

# Your 4 mathematically chosen champions
top_models = ['MPI-ESM1-2-LR', 'CanESM5', 'ACCESS-CM2', 'BCC-CSM2-MR']

def generate_daily_ensemble():
    print("🚀 Initializing Daily Multi-Model Ensembling (MME)...")
    
    model_dataframes = []
    
    for model in top_models:
        # Search for the CSV matching the model name inside the GMC_Daily_RainGauge folder
        search_pattern = os.path.join(input_dir, f"{model}_*.csv")
        file_list = glob.glob(search_pattern)
        
        if not file_list:
            print(f"❌ Could not find daily data for {model} in {input_dir}")
            continue
            
        # Grab the first matching file
        file_path = file_list[0]
        filename = os.path.basename(file_path)
        print(f"📥 Loading daily time-series: {filename}...")
        
        try:
            df = pd.read_csv(file_path)
            
            # Detect the Date column automatically
            date_col = None
            for col in ['Date', 'date', 'Time', 'time', 'DATE']:
                if col in df.columns:
                    date_col = col
                    break
                    
            if not date_col:
                print(f"⚠️ Could not find a 'Date' column in {model}. Found: {list(df.columns)}. Skipping!")
                continue
                
            # Convert to Datetime and set as index
            df[date_col] = pd.to_datetime(df[date_col])
            df.set_index(date_col, inplace=True)
            
            # Keep only the numeric grid points
            df = df.select_dtypes(include=['number'])
            
            model_dataframes.append(df)
            
        except Exception as e:
            print(f"⚠️ Error processing {model}: {e}")

    if len(model_dataframes) < len(top_models):
        print(f"\n⚠️ WARNING: Only loaded {len(model_dataframes)} out of {len(top_models)} models.")
        print("Please check your file names.")

    if not model_dataframes:
        print("❌ No valid model data was loaded. Exiting.")
        return

    print("\n⚙️ Calculating the Daily Multi-Model Mean across all 77 grid points...")
    
    # Concatenate the dataframes and calculate the mean for each day
    combined_df = pd.concat(model_dataframes)
    mme_df = combined_df.groupby(combined_df.index).mean()
    
    # Round to 2 decimal places
    mme_df = mme_df.round(2)
    
    # Save the final ensemble
    os.makedirs(os.path.dirname(output_file), exist_ok=True)
    mme_df.to_csv(output_file)
    
    print("\n✅ ENSEMBLE COMPLETE!")
    print(f"💾 Final Master MME saved to: {output_file}")
    print("\n📊 Quick preview of your final hydrological input data:")
    print(mme_df.head())

if __name__ == '__main__':
    generate_daily_ensemble()