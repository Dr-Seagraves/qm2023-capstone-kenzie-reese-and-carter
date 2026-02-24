"""
Fetch selected FRED series and save a quarterly aggregated CSV.

Defaults: `MORTGAGE30US`, `DGS10`, `CPIAUCSL`, `UNRATE`.

Requires: set environment variable `FRED_API_KEY` with your FRED API key.
If no API key is present, the script will exit with instructions.

Saves: `data/processed/fred_quarterly.csv`
"""
from pathlib import Path
import os
import pandas as pd
from config_paths import PROCESSED_DATA_DIR

DEFAULT_SERIES = [
    "MORTGAGE30US",  # 30-year fixed mortgage rates
    "DGS10",         # 10-year Treasury
    "CPIAUCSL",      # CPI-U
    "UNRATE",        # Unemployment rate
]


def fetch_series(fred_key: str, series: str) -> pd.Series:
    import requests

    url = "https://api.stlouisfed.org/fred/series/observations"
    params = {
        "series_id": series,
        "api_key": fred_key,
        "file_type": "json",
        "frequency": "m",
    }
    r = requests.get(url, params=params, timeout=30)
    r.raise_for_status()
    data = r.json()
    obs = data.get("observations", [])
    dates = [o["date"] for o in obs]
    values = [None if o["value"] == "." else float(o["value"]) for o in obs]
    s = pd.Series(values, index=pd.to_datetime(dates))
    s.name = series
    return s


def main(series_list=DEFAULT_SERIES):
    fred_key = os.environ.get("FRED_API_KEY")
    if not fred_key:
        print("FRED_API_KEY not found in environment.\n")
        print("Get a free key at https://fred.stlouisfed.org/docs/api/fred/ and set:\n")
        print("export FRED_API_KEY=your_key_here\n")
        return

    out_path = PROCESSED_DATA_DIR / "fred_quarterly.csv"

    frames = []
    for ser in series_list:
        print(f"Fetching {ser} from FRED...")
        s = fetch_series(fred_key, ser)
        # monthly to quarterly: take last observation in quarter
        q = s.resample('Q').last()
        frames.append(q)

    if not frames:
        print("No series fetched.")
        return

    df = pd.concat(frames, axis=1)
    df.index.name = 'date'
    df = df.sort_index()
    df.to_csv(out_path, index=True)
    print(f"Saved quarterly FRED series to: {out_path} (rows: {df.shape[0]}, cols: {df.shape[1]})")


if __name__ == "__main__":
    main()
