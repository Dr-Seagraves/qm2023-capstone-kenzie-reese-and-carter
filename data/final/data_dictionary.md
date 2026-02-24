# Data Dictionary

## Primary Datasets

### Metro Housing Prices (ZHVI)
- File: `metro_mortgage_panel.csv`
- Rows: 77673 (metros × quarters)
- Unique metros: 894
- Date range: 2000-03-31 00:00:00 to 2026-03-31 00:00:00
- Variables:
  - `RegionID`: Metro identifier
  - `RegionName`: Metro name
  - `StateName`: State
  - `date`: Quarter-end date
  - `price_index`: Zillow Home Value Index (ZHVI)

### REIT Returns & Fundamentals
- File: `reit_mortgage_panel.csv`
- Rows: 16323 (REITs × quarters)
- Unique REITs (tickers): 436
- Date range: 1986-10-01 00:00:00 to 2024-10-01 00:00:00
- Key variables: `ticker` (identifier), `usdprc` (price), `usdret` (returns), `market_equity`, `assets`, `roe`, `btm` (book-to-market)

### Mortgage Rates
- Variable: `MORTGAGE30US` (30-year fixed mortgage rate, %)
- Date range: 1971-06-30 00:00:00 to 2026-03-31 00:00:00
- Source: FRED (Board of Governors)

