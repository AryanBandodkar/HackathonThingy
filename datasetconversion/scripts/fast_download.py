import requests
from pathlib import Path
import time
from datetime import datetime, timedelta

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
RAW_DIR = REPO_ROOT / 'data' / 'rawNETCDF'
BASE_URL = "https://data-argo.ifremer.fr"


def get_recent_profile_urls(limit: int = 8) -> list:
    """Get URLs for recent NetCDF files from latest_data directory."""
    urls = []
    
    # Try recent dates (last 7 days)
    today = datetime.now()
    for days_back in range(7):
        date = today - timedelta(days=days_back)
        date_str = date.strftime("%Y%m%d")
        
        # Try different profile file patterns
        patterns = [
            f"D{date_str}_prof_0.nc",
            f"D{date_str}_prof_1.nc", 
            f"D{date_str}_prof.nc",
            f"R{date_str}_prof_0.nc",
            f"R{date_str}_prof_1.nc"
        ]
        
        for pattern in patterns:
            url = f"{BASE_URL}/latest_data/{pattern}"
            try:
                # Quick HEAD request to check if file exists
                response = requests.head(url, timeout=5, headers={'User-Agent': 'Mozilla/5.0'})
                if response.status_code == 200:
                    urls.append(url)
                    if len(urls) >= limit:
                        return urls
            except:
                continue
    
    # If no recent files found, try some known working patterns
    fallback_patterns = [
        "D20250101_prof_0.nc",
        "D20250102_prof_0.nc", 
        "D20250103_prof_0.nc"
    ]
    
    for pattern in fallback_patterns:
        url = f"{BASE_URL}/latest_data/{pattern}"
        try:
            response = requests.head(url, timeout=5, headers={'User-Agent': 'Mozilla/5.0'})
            if response.status_code == 200:
                urls.append(url)
                if len(urls) >= limit:
                    return urls
        except:
            continue
    
    return urls


def download_files(urls: list) -> None:
    RAW_DIR.mkdir(parents=True, exist_ok=True)
    print(f"Downloading {len(urls)} files...")
    start = time.time()
    for i, url in enumerate(urls, 1):
        filename = url.split("/")[-1]
        target = RAW_DIR / filename
        print(f"[{i}/{len(urls)}] {filename}...", end=" ", flush=True)
        try:
            with requests.get(
                url,
                timeout=60,
                stream=True,
                headers={"User-Agent": "Mozilla/5.0"},
                allow_redirects=True,
            ) as r:
                r.raise_for_status()
                with open(target, "wb") as fh:
                    for chunk in r.iter_content(chunk_size=1024 * 256):
                        if chunk:
                            fh.write(chunk)
            size_mb = target.stat().st_size / (1024 * 1024)
            print(f"[OK] {size_mb:.1f}MB")
        except Exception as exc:
            print(f"[FAIL] {exc}")
    elapsed = time.time() - start
    print(f"Done in {elapsed:.1f}s")


def main(limit: int = 8):
    print("Finding recent NetCDF files...")
    urls = get_recent_profile_urls(limit=limit)
    
    if not urls:
        print("No recent files found. Trying alternative approach...")
        # Try to find any available files by checking common patterns
        alternative_urls = []
        for i in range(10):
            url = f"{BASE_URL}/latest_data/D2025010{i}_prof_0.nc"
            try:
                response = requests.head(url, timeout=3, headers={'User-Agent': 'Mozilla/5.0'})
                if response.status_code == 200:
                    alternative_urls.append(url)
                    if len(alternative_urls) >= 3:
                        break
            except:
                continue
        urls = alternative_urls
    
    if urls:
        download_files(urls)
    else:
        print("No NetCDF files found. Please check the Argo data server.")


if __name__ == '__main__':
    main()
