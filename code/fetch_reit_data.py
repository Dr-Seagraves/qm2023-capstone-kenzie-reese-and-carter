"""
Fetch and clean primary REIT/HPI master dataset.

Behavior:
- Look for `reit_master.csv` in `data/raw/`; if missing, fall back to `hpi_master.csv`.
- Basic cleaning: drop full duplicates, drop rows missing entity or date columns, parse date if present.
- Saves cleaned file to `data/processed/reit_clean.csv`.

Usage: python code/fetch_reit_data.py
"""
from pathlib import Path
import pandas as pd
import numpy as np

from config_paths import RAW_DATA_DIR, PROCESSED_DATA_DIR


def detect_file():
    candidates = ["reit_master.csv", "reit_master_panel.csv", "hpi_master.csv", "hpi_master_panel.csv"]
    for fname in candidates:
        p = RAW_DATA_DIR / fname
        if p.exists():
            return p
    return None


def basic_clean(df: pd.DataFrame) -> pd.DataFrame:
    before = df.shape[0]
    # Drop exact duplicate rows
    df = df.drop_duplicates()

    # Try to detect an entity/id column and a date column
    cols = [c.lower() for c in df.columns]
    date_col = None
    id_col = None
    for c in df.columns:
        cl = c.lower()
        if cl in ("date", "month", "time") or "date" in cl:
            date_col = c
            break
    for c in df.columns:
        cl = c.lower()
        if cl in ("entity", "id", "region", "metro", "msa", "county", "zip"):
            id_col = c
            break

    if date_col is not None:
        try:
            df[date_col] = pd.to_datetime(df[date_col], errors="coerce")
        except Exception:
            pass

    # Drop rows missing both id and date (not useful for panel)
    if id_col is not None and date_col is not None:
        df = df[~(df[id_col].isna() & df[date_col].isna())]
    else:
        # If we can't find both, drop rows that are fully NA
        df = df.dropna(how="all")

    after = df.shape[0]
    print(f"Rows before de-dup/drop: {before}, after: {after}")
    return df


def main():
    src = detect_file()
    if src is None:
        print("No REIT or HPI master file found in data/raw/. Please add raw file and re-run.")
        return

    print(f"Loading primary file: {src}")
    df = pd.read_csv(src, low_memory=False)

    print("Initial shape:", df.shape)

    cleaned = basic_clean(df)

    # Save processed file
    out = PROCESSED_DATA_DIR / "reit_clean.csv"
    cleaned.to_csv(out, index=False)
    print(f"Saved cleaned primary dataset to: {out} (rows: {cleaned.shape[0]}, cols: {cleaned.shape[1]})")

    # Print a few summary statistics
    try:
        print("\n=== Summary statistics (numeric) ===")
        print(cleaned.select_dtypes(include=[np.number]).describe().transpose().head(10))
    except Exception:
        pass


if __name__ == "__main__":
    main()
