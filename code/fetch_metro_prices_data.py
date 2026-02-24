"""
Fetch and clean metro price data (Zillow ZHVI).

Reads Metro_zhvi_uc_sfrcondo_tier_0.33_0.67_sm_sa_month.csv in wide format and converts to long.
- Parse date columns to datetime
- Reshape from wide to long format (one row per metro-month)
- Aggregate to quarterly (take last month in quarter for each metro)
- Saves to data/processed/metro_prices_quarterly.csv

Usage: python code/fetch_metro_prices_data.py
"""
import pandas as pd
import numpy as np
from config_paths import RAW_DATA_DIR, PROCESSED_DATA_DIR


def main():
    src = RAW_DATA_DIR / "Metro_zhvi_uc_sfrcondo_tier_0.33_0.67_sm_sa_month.csv"
    
    if not src.exists():
        print(f"Metro prices file not found: {src}")
        return
    
    print(f"Loading metro prices data from: {src}")
    df = pd.read_csv(src)
    
    before = df.shape[0]
    print(f"Initial shape: {df.shape}")
    
    # Identify metadata columns vs date columns
    meta_cols = ['RegionID', 'SizeRank', 'RegionName', 'RegionType', 'StateName']
    date_cols = [c for c in df.columns if c not in meta_cols]
    
    print(f"Metadata columns: {meta_cols}")
    print(f"Date columns: {len(date_cols)} (from {date_cols[0]} to {date_cols[-1]})")
    
    # Melt to long format: each row = metro-month
    df_long = df.melt(
        id_vars=meta_cols,
        value_vars=date_cols,
        var_name='date',
        value_name='price_index'
    )
    
    # Parse date
    df_long['date'] = pd.to_datetime(df_long['date'])
    
    # Remove missing price indices
    df_long = df_long.dropna(subset=['price_index'])
    
    # Aggregate to quarterly per metro: take last observation in quarter
    df_long = df_long.sort_values(['RegionID', 'date'])
    df_q = df_long.groupby(['RegionID', 'RegionName', 'StateName', pd.Grouper(key='date', freq='QE-DEC')]).last(numeric_only=False).reset_index()
    
    # Save
    out = PROCESSED_DATA_DIR / "metro_prices_quarterly.csv"
    df_q.to_csv(out, index=False)
    
    print(f"Saved quarterly metro prices to: {out}")
    print(f"  Rows: {df_q.shape[0]}, Cols: {df_q.shape[1]}")
    print(f"  Date range: {df_q['date'].min()} to {df_q['date'].max()}")
    print(f"  Unique metros: {df_q['RegionID'].nunique()}")
    print(f"\nPrice index summary:")
    print(df_q['price_index'].describe())


if __name__ == "__main__":
    main()
