import netCDF4 as nc
import pandas as pd
from pathlib import Path
import logging

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

def save_to_csv(df, output_path, append_mode=False):
    """Save DataFrame to CSV, optionally append to existing file."""
    if df is not None and not df.empty:
        if append_mode and output_path.exists():
            # Append to existing CSV without header
            df.to_csv(output_path, mode='a', header=False, index=False)
            print(f"Appended to {output_path}")
        else:
            # Create new CSV with header
            df.to_csv(output_path, index=False)
            print(f"Saved to {output_path}")
    else:
        print(f"No data to save for {output_path}")

def main():
    repo_root = Path(__file__).resolve().parent.parent.parent
    logs_dir = repo_root / 'logs'
    logs_dir.mkdir(parents=True, exist_ok=True)
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s %(levelname)s %(message)s',
        handlers=[
            logging.FileHandler(logs_dir / 'etl.log', encoding='utf-8'),
            logging.StreamHandler()
        ]
    )
    input_dir = repo_root / 'data' / 'rawNETCDF'
    output_dir = repo_root / 'data' / 'processedCSV'
    output_dir.mkdir(parents=True, exist_ok=True)
    logging.info(f"Looking for NetCDF files in: {input_dir}")
    netcdf_files = sorted(list(input_dir.glob('*.nc')))
    logging.info(f"Found {len(netcdf_files)} files")

    # Use a single consolidated CSV file instead of per-profile files
    consolidated_csv = output_dir / "argo_profiles_consolidated.csv"
    
    # Check which files have already been processed
    processed_files = set()
    if consolidated_csv.exists():
        try:
            existing_df = pd.read_csv(consolidated_csv)
            if 'SOURCE_FILE' in existing_df.columns:
                processed_files = set(existing_df['SOURCE_FILE'].unique())
                logging.info(f"Found {len(processed_files)} already processed files")
        except Exception as exc:
            logging.warning(f"Could not read existing CSV: {exc}")
    
    new_files = [f for f in netcdf_files if f.name not in processed_files]
    logging.info(f"Processing {len(new_files)} new files out of {len(netcdf_files)} total")
    
    for file_path in new_files:
        logging.info(f"Processing file: {file_path.name}")
        try:
            with nc.Dataset(file_path, 'r') as ds:
                # Determine number of profiles from JULD or the first 2D variable
                n_prof = 0
                if 'JULD' in ds.variables:
                    n_prof = ds.variables['JULD'].shape[0]
                else:
                    # Fallback: infer from available 2D variable
                    for var in ['PRES', 'TEMP', 'PSAL', 'PRES_ADJUSTED', 'TEMP_ADJUSTED', 'PSAL_ADJUSTED']:
                        if var in ds.variables and len(ds.variables[var].shape) >= 2:
                            n_prof = ds.variables[var].shape[0]
                            break
                logging.info(f"  Profiles detected: {n_prof}")

            for profile_idx in range(n_prof):
                data = extract_profile(file_path, profile_idx)
                if data:
                    df = transform_data(data)
                    # Add source file info
                    df['SOURCE_FILE'] = file_path.name
                    # Append to consolidated CSV
                    save_to_csv(df, consolidated_csv, append_mode=True)
                else:
                    logging.warning(f"  Skipping profile {profile_idx}: No data extracted")
        except Exception as exc:
            logging.error(f"Failed to process {file_path.name}: {exc}")
    
    logging.info(f"All profiles consolidated into: {consolidated_csv}")

if __name__ == "__main__":
    main()

