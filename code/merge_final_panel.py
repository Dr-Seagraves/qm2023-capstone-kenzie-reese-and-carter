"""
Merge processed datasets to build analysis-ready panel.

Behavior:
- Reads `data/processed/reit_clean.csv`, `data/processed/mortgage_quarterly.csv`, 
  and `data/processed/metro_prices_quarterly.csv`.
- Processes each and merges at quarterly level:
  - REIT: ticker × quarter
  - Metro prices: RegionID × quarter  
  - Mortgage: national × quarter
- Produces two output files:
  - hpi_mortgage_panel.csv (metro prices × mortgage rates)
  - reit_mortgage_panel.csv (REIT × mortgage rates)

Usage: python3 code/merge_final_panel.py
"""
from pathlib import Path
import pandas as pd
import numpy as np
from config_paths import PROCESSED_DATA_DIR, FINAL_DATA_DIR


def load_reit(path: Path) -> pd.DataFrame:
    """Load and process REIT data to quarterly ticker-level."""
    if not path.exists():
        print(f"REIT file not found: {path}")
        return pd.DataFrame()
    
    df = pd.read_csv(path, low_memory=False)
    print(f"REIT shape: {df.shape}")
    
    # Parse date
    if 'date' in df.columns:
        df['date'] = pd.to_datetime(df['date'], errors='coerce')
    
    # Create quarter-end date
    df['quarter'] = df['date'].dt.to_period('Q')
    df['date'] = df['quarter'].dt.to_timestamp()
    
    # Group by ticker and quarter, taking last observation
    group_cols = ['ticker', 'permno', 'date']
    df_q = df.sort_values('date').groupby(group_cols).last(numeric_only=False).reset_index()
    
    print(f"REIT quarterly shape: {df_q.shape}")
    return df_q


def load_metro_prices(path: Path) -> pd.DataFrame:
    """Load metro prices quarterly data."""
    if not path.exists():
        print(f"Metro prices file not found: {path}")
        return pd.DataFrame()
    
    df = pd.read_csv(path)
    # Ensure date is datetime
    df['date'] = pd.to_datetime(df['date'])
    print(f"Metro prices quarterly shape: {df.shape}")
    return df


def load_mortgage(path: Path) -> pd.DataFrame:
    """Load mortgage rates quarterly data."""
    if not path.exists():
        print(f"Mortgage file not found: {path}")
        return pd.DataFrame()
    
    df = pd.read_csv(path)
    df['date'] = pd.to_datetime(df['date'])
    print(f"Mortgage quarterly shape: {df.shape}")
    return df


def main():
    reit_path = PROCESSED_DATA_DIR / 'reit_clean.csv'
    metro_path = PROCESSED_DATA_DIR / 'metro_prices_quarterly.csv'
    mortgage_path = PROCESSED_DATA_DIR / 'mortgage_quarterly.csv'
    
    print("=" * 60)
    print("LOADING DATA")
    print("=" * 60)
    
    reit = load_reit(reit_path)
    metro = load_metro_prices(metro_path)
    mortgage = load_mortgage(mortgage_path)
    
    # Panel 1: Metro prices + mortgage rates
    print("\n" + "=" * 60)
    print("Merging metro prices + mortgage rates")
    print("=" * 60)
    
    if not metro.empty and not mortgage.empty:
        panel_metro = metro.merge(mortgage, on='date', how='left')
        out_metro = FINAL_DATA_DIR / 'metro_mortgage_panel.csv'
        panel_metro.to_csv(out_metro, index=False)
        print(f"Saved to: {out_metro}")
        print(f"  Shape: {panel_metro.shape}")
        print(f"  Columns: {panel_metro.columns.tolist()}")
    else:
        if not metro.empty:
            out_metro = FINAL_DATA_DIR / 'metro_mortgage_panel.csv'
            metro.to_csv(out_metro, index=False)
            print(f"Saved metro prices (no mortgage data) to: {out_metro}")
    
    # Panel 2: REIT + mortgage rates
    print("\n" + "=" * 60)
    print("Merging REIT + mortgage rates")
    print("=" * 60)
    
    if not reit.empty and not mortgage.empty:
        panel_reit = reit.merge(mortgage, on='date', how='left')
        out_reit = FINAL_DATA_DIR / 'reit_mortgage_panel.csv'
        panel_reit.to_csv(out_reit, index=False)
        print(f"Saved to: {out_reit}")
        print(f"  Shape: {panel_reit.shape}")
        print(f"  Columns: {panel_reit.columns.tolist()}")
    else:
        if not reit.empty:
            out_reit = FINAL_DATA_DIR / 'reit_mortgage_panel.csv'
            reit.to_csv(out_reit, index=False)
            print(f"Saved REIT (no mortgage data) to: {out_reit}")
    
    # Update data dictionary
    print("\n" + "=" * 60)
    print("Writing data dictionary")
    print("=" * 60)
    
    dict_path = FINAL_DATA_DIR / 'data_dictionary.md'
    with open(dict_path, 'w') as f:
        f.write('# Data Dictionary\n\n')
        f.write('## Primary Datasets\n\n')
        
        if not metro.empty:
            f.write('### Metro Housing Prices (ZHVI)\n')
            f.write(f'- File: `metro_mortgage_panel.csv`\n')
            f.write(f'- Rows: {metro.shape[0]} (metros × quarters)\n')
            f.write(f'- Unique metros: {metro["RegionID"].nunique()}\n')
            f.write(f'- Date range: {metro["date"].min()} to {metro["date"].max()}\n')
            f.write('- Variables:\n')
            f.write('  - `RegionID`: Metro identifier\n')
            f.write('  - `RegionName`: Metro name\n')
            f.write('  - `StateName`: State\n')
            f.write('  - `date`: Quarter-end date\n')
            f.write('  - `price_index`: Zillow Home Value Index (ZHVI)\n\n')
        
        if not reit.empty:
            f.write('### REIT Returns & Fundamentals\n')
            f.write(f'- File: `reit_mortgage_panel.csv`\n')
            f.write(f'- Rows: {reit.shape[0]} (REITs × quarters)\n')
            f.write(f'- Unique REITs (tickers): {reit["ticker"].nunique()}\n')
            f.write(f'- Date range: {reit["date"].min()} to {reit["date"].max()}\n')
            f.write('- Key variables: `ticker` (identifier), `usdprc` (price), `usdret` (returns), ')
            f.write('`market_equity`, `assets`, `roe`, `btm` (book-to-market)\n\n')
        
        f.write('### Mortgage Rates\n')
        f.write('- Variable: `MORTGAGE30US` (30-year fixed mortgage rate, %)\n')
        f.write(f'- Date range: {mortgage["date"].min()} to {mortgage["date"].max()}\n')
        f.write('- Source: FRED (Board of Governors)\n\n')
    
    print(f"Saved data dictionary to: {dict_path}")


if __name__ == '__main__':
    main()
