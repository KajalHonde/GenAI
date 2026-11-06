"""Download official NDMA pages into data/raw/."""
from pathlib import Path
import requests

ROOT = Path(__file__).resolve().parent.parent
RAW_DIR = ROOT / "data" / "raw"

SOURCES = {
    "ndma_guidelines.html": "https://ndma.gov.in/en/guidelines",
    "flood_dos_donts.html": "https://ndma.gov.in/en/floods-dos-donts",
    "ndma_home.html": "https://ndma.gov.in/en",
}

def download_documents():
    RAW_DIR.mkdir(parents=True, exist_ok=True)
    results = []
    headers = {"User-Agent": "AapdaMitra-Student-Project/1.0"}

    for filename, url in SOURCES.items():
        destination = RAW_DIR / filename
        try:
            response = requests.get(url, headers=headers, timeout=(10, 30))
            response.raise_for_status()
            destination.write_bytes(response.content)
            print(f"[OK] Downloaded {filename}")
            results.append((filename, True))
        except requests.RequestException as exc:
            print(f"[ERROR] Download failed for {url}: {exc}")
            results.append((filename, False))
        except OSError as exc:
            print(f"[ERROR] Could not save {destination}: {exc}")
            results.append((filename, False))

    return results

if __name__ == "__main__":
    results = download_documents()
    successful = sum(ok for _, ok in results)
    print(f"Downloaded {successful} of {len(SOURCES)} pages.")
    if successful == 0:
        raise SystemExit("No pages downloaded. Check internet access and retry.")
