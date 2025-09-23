import requests
from pathlib import Path
import time

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
RAW_DIR = REPO_ROOT / 'data' / 'rawNETCDF'

def main():
    RAW_DIR.mkdir(parents=True, exist_ok=True)
    
    # Download smaller, faster files (these are typically smaller)
    urls = [
        "https://data-argo.ifremer.fr/latest_data/D20250624_prof_0.nc",
        "https://data-argo.ifremer.fr/latest_data/D20250623_prof_0.nc"
    ]
    
    print(f"Downloading {len(urls)} files...")
    start = time.time()
    
    for i, url in enumerate(urls, 1):
        filename = url.split('/')[-1]
        target = RAW_DIR / filename
        
        print(f"[{i}/{len(urls)}] {filename}...", end=" ", flush=True)
        try:
            # Optimized request settings
            response = requests.get(
                url, 
                timeout=10,  # Even shorter timeout
                stream=False,  # Load all at once for small files
                headers={'User-Agent': 'Mozilla/5.0'},  # Some servers block default UA
                allow_redirects=True
            )
            response.raise_for_status()
            
            target.write_bytes(response.content)
            size_mb = len(response.content) / (1024 * 1024)
            print(f"[OK] {size_mb:.1f}MB")
            
        except Exception as exc:
            print(f"[FAIL] {exc}")
    
    elapsed = time.time() - start
    print(f"Done in {elapsed:.1f}s")

if __name__ == '__main__':
    main()
