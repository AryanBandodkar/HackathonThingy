import netCDF4 as nc
from pathlib import Path

def _print_header(title: str) -> None:
    print("=" * 80)
    print(title)
    print("=" * 80)


def inspect_netcdf(file_path):
    """Inspect a NetCDF file and print key information."""
    try:
        with nc.Dataset(file_path, 'r') as ds:
            _print_header(f"Inspecting: {Path(file_path).name}")
            print("Dimensions:")
            for name, dim in ds.dimensions.items():
                print(f"  - {name}: size={len(dim)}")

            print("\nVariables:")
            for name, var in ds.variables.items():
                dims = ",".join(var.dimensions)
                print(f"  - {name}: dims=({dims}), shape={var.shape}, dtype={getattr(var, 'dtype', None)}")

            print("\nGlobal attributes:")
            for attr_name in ds.ncattrs():
                print(f"  - {attr_name} = {getattr(ds, attr_name)}")

            print("\nKey variables (shapes and first 5 samples):")
            for var_name in ['TEMP', 'PSAL', 'PRES', 'LATITUDE', 'LONGITUDE']:
                if var_name in ds.variables:
                    var = ds.variables[var_name]
                    print(f"  * {var_name}: shape={var.shape}")
                    try:
                        data = var[:].ravel()[:5]
                        print(f"    samples: {data.tolist()}")
                    except Exception as exc:
                        print(f"    (unable to preview values: {exc})")
                else:
                    print(f"  * {var_name}: NOT PRESENT")
    except Exception as e:
        print(f"Error reading {file_path}: {e}")

def main(files=None):
    data_dir = Path(__file__).resolve().parent.parent.parent / 'data' / 'rawNETCDF'
    data_dir.mkdir(parents=True, exist_ok=True)
    print(f"Looking for .nc files in: {data_dir}")

    targets = None
    if files:
        targets = [Path(f) if Path(f).is_absolute() else (data_dir / f) for f in files]
    else:
        targets = sorted(list(data_dir.glob('*.nc')))

    if not targets:
        print("No NetCDF files found.")
        return

    print(f"Found {len(targets)} file(s)")
    for fp in targets:
        inspect_netcdf(fp)

if __name__ == "__main__":
    import sys
    main(sys.argv[1:] if len(sys.argv) > 1 else None)
