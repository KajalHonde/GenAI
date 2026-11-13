
from pathlib import Path
import requests

RAW_DIR = Path("data/raw")

SOURCES = {
    "guidelines.html": "https://ndma.gov.in/en/guidelines",
    "flood_dos_donts.html": "https://ndma.gov.in/en/floods-dos-donts",
    "ndma_home.html": "https://ndma.gov.in/en",
}


def fetch_pages():
    RAW_DIR.mkdir(parents=True, exist_ok=True)

    for filename, url in SOURCES.items():
        try:
            print(f"Downloading: {url}")

            response = requests.get(
                url,
                timeout=20,
                headers={"User-Agent": "Mozilla/5.0"}
            )

            response.raise_for_status()

            file_path = RAW_DIR / filename
            file_path.write_text(
                response.text,
                encoding="utf-8"
            )

            print(f"Saved: {file_path}")

        except requests.exceptions.Timeout:
            print(f"Timeout error: {url}")

        except requests.exceptions.RequestException as error:
            print(f"Download failed: {url}")
            print(error)


if __name__ == "__main__":
    fetch_pages()
