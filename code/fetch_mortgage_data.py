"""
Fetch and clean mortgage rate data (MORTGAGE30US).

Reads MORTGAGE30US.csv (weekly mortgage rates) and aggregates to quarterly.
- Parse observation_date to datetime
- Aggregate to quarterly (take mean of weekly rates in quarter)
- Saves to data/processed/mortgage_quarterly.csv

Usage: python code/fetch_mortgage_data.py
"""
import pandas as pd
from config_paths import RAW_DATA_DIR, PROCESSED_DATA_DIR


def main():
    src = RAW_DATA_DIR / "MORTGAGE30US.csv"
    
    if not src.exists():
        print(f"Mortgage file not found: {src}")
        return
    
    print(f"Loading mortgage data from: {src}")
    df = pd.read_csv(src)
    
    before = df.shape[0]
    print(f"Initial shape: {df.shape}")
    
    # Parse date
    if 'observation_date' in df.columns:
        df['date'] = pd.to_datetime(df['observation_date'])
    else:
        print("No observation_date column found.")
        return
    
    # Remove rows with missing rates
    df = df.dropna(subset=['MORTGAGE30US'])
    
    after = df.shape[0]
    print(f"Rows after removing NAs: {after} ({before-after} removed)")
    
    # Aggregate to quarterly: take mean of weekly observations
    df_q = df.set_index('date').resample('QE-DEC').agg({
        'MORTGAGE30US': 'mean'
    }).reset_index()
    
    # Save
    out = PROCESSED_DATA_DIR / "mortgage_quarterly.csv"
    df_q.to_csv(out, index=False)
    print(f"Saved quarterly mortgage data to: {out} (rows: {df_q.shape[0]}, cols: {df_q.shape[1]})")
    print(f"Date range: {df_q['date'].min()} to {df_q['date'].max()}")
    print(f"\nMortgage rate summary:")
    print(df_q['MORTGAGE30US'].describe())


if __name__ == "__main__":
    main()
