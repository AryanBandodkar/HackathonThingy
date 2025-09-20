import netCDF4 as nc
from pathlib import Path

def inspect_netcdf(file_path):
    """Inspect a NetCDF file and print key information."""
    try:
        with nc.Dataset(file_path, 'r') as ds:
            print(f"\nFile: {file_path}")
            print("Variables:", list(ds.variables.keys()))
            print("Dimensions:", list(ds.dimensions.keys()))
            print("Global attributes:", list(ds.ncattrs()))
            
            # Inspect key variables
            for var in ['TEMP', 'PSAL', 'PRES', 'LATITUDE', 'LONGITUDE']:
                if var in ds.variables:
                    print(f"{var} shape:", ds.variables[var][:].shape)
                    print(f"{var} sample values:", ds.variables[var][:].flatten()[:5])
    except Exception as e:
        print(f"Error reading {file_path}: {e}")

def main():
    data_dir = Path(__file__).resolve().parent.parent.parent / 'data' / 'rawNETCDF'
    print(f"Looking for files in: {data_dir}")
    files = ['D1900722_001.nc', 'D5906300_001.nc']
    
    for file in files:
        file_path = data_dir / file
        if file_path.exists():
            inspect_netcdf(file_path)
        else:
            print(f"File not found: {file_path}")

if __name__ == "__main__":
    main()
