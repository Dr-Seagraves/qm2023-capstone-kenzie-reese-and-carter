"""
Merge processed primary HPI dataset with quarterly FRED series to build analysis-ready panel.

Behavior:
- Reads `data/processed/reit_clean.csv` and `data/processed/fred_quarterly.csv`.
- Converts HPI monthly observations to quarterly (takes last month in quarter).
- For each place_id/place_name × quarter creates a row with `index` (prefers `index_sa` otherwise `index_nsa`).
- Merges FRED quarterly data on `date` (quarter end timestamp).
- Saves `data/final/hpi_mortgage_panel.csv` and a small data dictionary stub.

Usage: python3 code/merge_final_panel.py
"""
from pathlib import Path
import pandas as pd
import numpy as np

from config_paths import PROCESSED_DATA_DIR, FINAL_DATA_DIR


def load_hpi(path: Path) -> pd.DataFrame:
    df = pd.read_csv(path, low_memory=False)
    # Create a datetime from yr + period (period is month number)
    if 'yr' in df.columns and 'period' in df.columns:
        df['month'] = df['period'].astype(int)
        # pandas requires columns named 'year' and 'month' when assembling
        tmp = df[['yr', 'month']].rename(columns={'yr': 'year'})
        df['date'] = pd.to_datetime(tmp.assign(day=1))
        # Convert to quarter-end timestamp
        df['date'] = df['date'].dt.to_period('Q').dt.to_timestamp('Q')
    else:
        # try to find a date-like column
        for c in df.columns:
            if 'date' in c.lower():
                df['date'] = pd.to_datetime(df[c], errors='coerce')
                df['date'] = df['date'].dt.to_period('Q').dt.to_timestamp('Q')
                break

    # Choose index column
    if 'index_sa' in df.columns:
        df['index'] = df['index_sa']
    elif 'index_nsa' in df.columns:
        df['index'] = df['index_nsa']
    else:
        # pick first numeric column
        numcols = df.select_dtypes(include=[np.number]).columns.tolist()
        if numcols:
            df['index'] = df[numcols[0]]

    # Keep only last observation per place_id × quarter
    group_cols = []
    if 'place_id' in df.columns:
        group_cols = ['place_id', 'date']
    elif 'place_name' in df.columns:
        group_cols = ['place_name', 'date']
    else:
        group_cols = ['date']

    df_q = df.sort_values('date').groupby(group_cols).last().reset_index()
    # Ensure place_id and place_name exist
    if 'place_id' not in df_q.columns and 'place_name' in df_q.columns:
        df_q['place_id'] = df_q['place_name']

    return df_q


def load_fred(path: Path) -> pd.DataFrame:
    if not path.exists():
        print(f"FRED file not found at {path}. Run code/fetch_fred_data.py first.")
        return pd.DataFrame()
    df = pd.read_csv(path, parse_dates=['date'], index_col='date')
    df = df.sort_index()
    df = df.reset_index()
    return df


def main():
    hpi_path = PROCESSED_DATA_DIR / 'reit_clean.csv'
    fred_path = PROCESSED_DATA_DIR / 'fred_quarterly.csv'

    print(f"Loading HPI from: {hpi_path}")
    hpi = load_hpi(hpi_path)
    print(f"HPI quarterly shape: {hpi.shape}")

    fred = load_fred(fred_path)
    if fred.empty:
        print("No FRED data found; the panel will contain only HPI variables.")

    # Merge: cross-join by date (i.e., attach same FRED row to each place-date)
    if not fred.empty:
        merged = hpi.merge(fred, on='date', how='left')
    else:
        merged = hpi.copy()

    out = FINAL_DATA_DIR / 'hpi_mortgage_panel.csv'
    merged.to_csv(out, index=False)
    print(f"Saved merged panel to: {out} (rows: {merged.shape[0]}, cols: {merged.shape[1]})")

    # Create a minimal data dictionary stub
    dict_path = FINAL_DATA_DIR / 'data_dictionary.md'
    with open(dict_path, 'w') as f:
        f.write('# Data Dictionary\n\n')
        f.write(f'- Panel rows: {merged.shape[0]}\n')
        f.write(f'- Panel columns: {merged.shape[1]}\n\n')
        f.write('Variables:\n')
        f.write('- `place_id`: entity identifier (from HPI)\n')
        f.write('- `place_name`: human-readable place name\n')
        f.write('- `date`: quarter-end date (YYYY-MM-DD)\n')
        f.write('- `index`: HPI index (seasonally adjusted preferred)\n')
        f.write('- `MORTGAGE30US`, `DGS10`, `CPIAUCSL`, `UNRATE`: FRED quarterly series (when available)\n')


if __name__ == '__main__':
    main()
