import netCDF4 as nc
import pandas as pd
from pathlib import Path

def extract_profile(file_path, profile_idx=0):
    """Extract key variables from a NetCDF file for a specific profile."""
    try:
        with nc.Dataset(file_path, 'r') as ds:
            data = {}
            # Extract 1D variables (per profile)
            for var in ['JULD', 'LATITUDE', 'LONGITUDE']:
                if var in ds.variables:
                    data[var] = ds.variables[var][profile_idx]
                else:
                    data[var] = None
            # Extract 2D variables (profile x level)
            for var in ['PRES', 'TEMP', 'PSAL', 'PRES_ADJUSTED', 'TEMP_ADJUSTED', 'PSAL_ADJUSTED']:
                if var in ds.variables:
                    data[var] = ds.variables[var][profile_idx, :].flatten()
                else:
                    data[var] = []
            # Add profile and level indices
            n_levels = len(data['PRES']) if data['PRES'] is not None else 0
            data['N_PROF'] = [profile_idx] * n_levels
            data['N_LEVELS'] = list(range(n_levels))
            return data
    except Exception as e:
        print(f"Error processing {file_path}: {e}")
        return None

def transform_data(data):
    """Transform extracted data into a DataFrame with all requested columns."""
    n = len(data['N_LEVELS'])
    return pd.DataFrame({
        'N_PROF': data['N_PROF'],
        'N_LEVELS': data['N_LEVELS'],
        'JULD': [data['JULD']] * n,
        'LATITUDE': [data['LATITUDE']] * n,
        'LONGITUDE': [data['LONGITUDE']] * n,
        'PRES': data['PRES'],
        'TEMP': data['TEMP'],
        'PSAL': data['PSAL'],
        'PRES_ADJUSTED': data['PRES_ADJUSTED'],
        'TEMP_ADJUSTED': data['TEMP_ADJUSTED'],
        'PSAL_ADJUSTED': data['PSAL_ADJUSTED'],
    })

def save_to_csv(df, output_path):
    """Save DataFrame to CSV."""
    if df is not None and not df.empty:
        df.to_csv(output_path, index=False)
        print(f"Saved to {output_path}")
    else:
        print(f"No data to save for {output_path}")

def main():
    input_dir = Path(__file__).resolve().parent.parent.parent / 'data' / 'rawNETCDF'
    output_dir = Path(__file__).resolve().parent.parent.parent / 'data' / 'processedCSV'
    output_dir.mkdir(parents=True, exist_ok=True)
    print(f"Looking for files in: {input_dir}")
    print("Files found:", [f.name for f in input_dir.glob("*")])
    
    files = ['D1900722_001.nc','D5906300_001.nc']
    for file in files:
        file_path = input_dir / file
        if file_path.exists():
            for profile_idx in range(2):  # Process both profiles
                data = extract_profile(file_path, profile_idx)
                if data:
                    df = transform_data(data)
                    output_path = output_dir / f"{file_path.stem}_profile{profile_idx}_processed.csv"
                    save_to_csv(df, output_path)
                else:
                    print(f"Skipping {file} (profile {profile_idx}): No data extracted")
        else:
            print(f"File not found: {file_path}")

if __name__ == "__main__":
    main()

