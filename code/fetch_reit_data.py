"""
Fetch and clean primary REIT dataset.

Reads REIT_sample_2000_2024_All_Variables.csv and cleans for further analysis.
- Handles missing values and duplicates
- Parses date to datetime
- Saves to data/processed/reit_clean.csv

Usage: python code/fetch_reit_data.py
"""
from pathlib import Path
import pandas as pd
import numpy as np

from config_paths import RAW_DATA_DIR, PROCESSED_DATA_DIR


def main():
    src = RAW_DATA_DIR / "REIT_sample_2000_2024_All_Variables.csv"
    
    if not src.exists():
        print(f"REIT file not found: {src}")
        return
    
    print(f"Loading REIT data from: {src}")
    df = pd.read_csv(src, low_memory=False)
    
    before = df.shape[0]
    print(f"Initial shape: {df.shape}")
    
    # Parse date column
    if 'date' in df.columns:
        df['date'] = pd.to_datetime(df['date'], errors='coerce')
    
    # Drop exact duplicates
    df = df.drop_duplicates()
    
    # Drop rows where both date and permno are missing (not useful)
    df = df.dropna(subset=['date', 'permno'], how='any')
    
    after = df.shape[0]
    print(f"Rows before cleaning: {before}, after: {after} ({before-after} removed)")
    
    # Save processed file
    out = PROCESSED_DATA_DIR / "reit_clean.csv"
    df.to_csv(out, index=False)
    print(f"Saved cleaned REIT data to: {out} (rows: {df.shape[0]}, cols: {df.shape[1]})")
    
    # Print summary statistics for numeric columns
    try:
        print("\n=== Summary statistics (numeric) ===")
        numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
        print(f"Numeric columns: {numeric_cols}")
        print(df[numeric_cols].describe().iloc[:5].to_string())
    except Exception as e:
        print(f"Could not print summary stats: {e}")


if __name__ == "__main__":
    main()
