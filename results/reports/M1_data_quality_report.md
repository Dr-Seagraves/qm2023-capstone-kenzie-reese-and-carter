# M1 Data Quality Report

## Executive Summary

This report documents the data pipeline for Milestone 1 of the QM 2023 Capstone project. The analysis examines the sensitivity of regional home prices (via REIT returns and metro Zillow indices) to mortgage rate changes. The final dataset combines:
- **REIT returns and fundamentals** (48,019 observations → 16,323 quarterly)
- **Metro housing price indices** (77,673 metro-quarter observations)
- **National mortgage rates** (220 quarterly observations)

---

## 1. Data Sources

### 1.1 Primary Dataset: REIT Sample (2000–2024)
- **File**: `data/raw/REIT_sample_2000_2024_All_Variables.csv`
- **Records**: 48,019 REIT-date observations (2000–2024)
- **Key Variables**: 
  - `ticker`, `permno`: REIT identifiers
  - `date`: Observation date
  - `usdret`: Monthly USD returns
  - `usdprc`: Stock price
  - `market_equity`, `assets`, `roe`, `btm`, `beta`: Fundamentals
- **Source**: Provided by course staff (Compustat/CRSP merged)

### 1.2 Secondary Dataset: Metro Zillow ZHVI
- **File**: `data/raw/Metro_zhvi_uc_sfrcondo_tier_0.33_0.67_sm_sa_month.csv`
- **Records**: 895 metro areas × 313 months (2000–2026)
- **Key Variables**:
  - `RegionID`, `RegionName`, `StateName`: Metro identifiers
  - Monthly price indices (Zillow Home Value Index, ZHVI)
- **Source**: Zillow Research (public data)
- **Selection Rationale**: Mid-tier single-family + condo prices capture typical residential markets

### 1.3 Tertiary Dataset: Mortgage Rates
- **File**: `data/raw/MORTGAGE30US.csv`
- **Records**: 2,865 weekly observations (1971–2026)
- **Variable**: `MORTGAGE30US` (30-year fixed mortgage rate %)
- **Source**: FRED (Board of Governors, series ID MORTGAGE30US)
- **Selection Rationale**: Primary driver of housing affordability; directly affects REIT valuations

---

## 2. Data Cleaning & Processing

### 2.1 REIT Data Cleaning
**Script**: `code/fetch_reit_data.py`

| Step | Input Rows | Output Rows | Details |
|------|-----------|-----------|---------|
| Initial load | 48,019 | 48,019 | No duplicates detected |
| Drop missing date/permno | 48,019 | 48,019 | All records had valid date + permno |
| Final cleaned CSV | — | 48,019 | Output: `data/processed/reit_clean.csv` |

**Processing Logic**:
- Parsed `date` column to datetime format
- Removed exact duplicate rows (none found)
- Dropped records missing both `date` and `permno` (none found)
- Kept all 22 original columns for downstream analysis

**Outcome**: 48,019 REIT-month observations ready for quarterly aggregation

### 2.2 Mortgage Rates Cleaning
**Script**: `code/fetch_mortgage_data.py`

| Step | Input Rows | Output Rows | Details |
|------|-----------|-----------|---------|
| Initial load | 2,865 | 2,865 | Weekly observations from 1971–2026 |
| Drop missing rates | 2,865 | 2,865 | No missing values |
| Aggregate to quarterly mean | — | 220 | Take mean of weekly rates per quarter |

**Processing Logic**:
- Parsed `observation_date` to datetime
- Removed missing rate values (none found in weekly data)
- Aggregated to quarterly frequency (take mean of all weeks in each quarter)
- Output: `data/processed/mortgage_quarterly.csv`

**Outcome**: Quarterly mortgage rate time series (1971 Q2 – 2026 Q1), 220 observations

### 2.3 Metro Price Data Cleaning
**Script**: `code/fetch_metro_prices_data.py`

| Step | Input Rows | Output Rows | Details |
|------|-----------|-----------|---------|
| Initial load (wide) | 895 metros | — | 313 monthly date columns (2000–2026) |
| Reshape to long | — | 280,135 metro-months | One row per region × month |
| Drop missing prices | 280,135 | 77,673 | Remove metros with no data in that quarter |
| Aggregate to quarterly | — | 77,673 | Take last month's price per metro-quarter (Q 2000 Q1 – 2026 Q1) |

**Processing Logic**:
- Melted wide date format (columns) to long format (rows)
- Parsed date column to datetime
- Removed metro-month observations with missing price indices
- Aggregated to quarterly: took the last observation in each quarter per metro (captures end-of-period valuation)
- Output: `data/processed/metro_prices_quarterly.csv`

**Outcome**: 77,673 metro-quarter observations (894 unique metros × ~87 quarters)

---

## 3. Merge Strategy & Panel Construction

**Script**: `code/merge_final_panel.py`

### 3.1 REIT + Mortgage Rates Panel

**Process**:
1. Load `reit_clean.csv` (48,019 REIT-months)
2. Aggregate REIT to quarterly:
   - Group by `ticker`, `permno`, and quarter-end date
   - Take last observation per ticker-quarter
   - Result: 16,323 REIT-quarter observations
3. Load `mortgage_quarterly.csv` (220 quarters)
4. **Left merge** REIT onto mortgage rates by date
   - Retains all 16,323 REIT-quarter observations
   - Attaches national mortgage rate (or NA if date not in 1971–2026 range)
   - Result: `reit_mortgage_panel.csv` (16,323 rows, 24 columns)

**Merge Verification**:
- ✅ No row loss (REIT: 16,323 → 16,323)
- ✅ All REIT observations retained (left join)
- ✅ Mortgage rates successfully matched for dates 2000–2024

### 3.2 Metro + Mortgage Rates Panel

**Process**:
1. Load `metro_prices_quarterly.csv` (77,673 metro-quarters)
2. Load `mortgage_quarterly.csv` (220 quarters)
3. **Left merge** metro onto mortgage by date
   - Retains all 77,673 metro-quarter observations
   - Attaches national mortgage rate
   - Result: `metro_mortgage_panel.csv` (77,673 rows, 8 columns)

**Merge Verification**:
- ✅ No row loss (metro: 77,673 → 77,673)
- ✅ All metro observations retained (left join)
- ✅ Mortgage rates successfully matched for all quarters (2000 Q1 – 2026 Q1)

---

## 4. Final Dataset Dimensions

### 4.1 REIT-Mortgage Panel
- **File**: `data/final/reit_mortgage_panel.csv`
- **Rows**: 16,323 (REITs × quarters)
- **Columns**: 24
  - Identifiers: `ticker`, `permno`
  - Time: `date` (quarter-end), `quarter`
  - REIT fundamentals: `usdprc`, `usdret`, `market_equity`, `assets`, `roe`, `btm`, `beta`
  - Macro: `MORTGAGE30US`
- **Date range**: 2000 Q1 – 2024 Q4
- **Unique entities**: 27 unique tickers

### 4.2 Metro-Mortgage Panel
- **File**: `data/final/metro_mortgage_panel.csv`
- **Rows**: 77,673 (metros × quarters)
- **Columns**: 8
  - Identifiers: `RegionID`, `RegionName`, `StateName`
  - Metadata: `SizeRank`, `RegionType`
  - Price: `price_index` (Zillow ZHVI)
  - Macro: `MORTGAGE30US`
- **Date range**: 2000 Q1 – 2026 Q1
- **Unique entities**: 894 metro areas

---

## 5. Data Quality Assessment

### 5.1 Completeness

| Dataset | Records | Missing Values | % Complete |
|---------|---------|---|---|
| REIT fundamentals (`assets`, `roe`) | 16,323 | ~1,500 | 90.8% |
| REIT returns (`usdret`) | 16,323 | 628 | 96.2% |
| Metro ZHVI prices | 77,673 | 0 | 100% |
| Mortgage rates (Q 2000+) | 77,673 | 0 | 100% |

### 5.2 Outliers & Data Issues

**REIT Data**:
- Extreme returns: Min = –79.8%, Max = +798% (winsorize at 1%/99% for analysis)
- Missing fundamentals in early years of REIT history (before financial reporting mandatory)
- Resolved: Keep as-is; analysis can exclude or impute

**Metro Prices**:
- Zillow ZHVI only available 2000 Q1 onwards (pre-2000 data sparse)
- Some metros have sparse quarterly history (resort/specialty markets)
- Ultra-high values: Max $1.59M (likely luxury markets; verify in sensitivity analysis)

**Mortgage Rates**:
- Weekly data aggregated to quarterly mean (smooth rate changes)
- Historical lows: 2.76% (2021–2022)
- Historical highs: 17.74% (1981, outside REIT panel dates)

### 5.3 Merge Integrity

✅ **No row loss** in left merges (all REIT and metro observations retained)  
✅ **Key alignment** verified (date columns matched accurately)  
✅ **Duplicate free** (quarterly aggregation unique by entity × quarter)  
✅ **Long format panel** ready for regression analysis

---

## 6. Economic Justification for Cleaning Decisions

1. **Quarterly Aggregation**: 
   - REITs trade daily but file quarterly earnings; quarterly HPI more stable
   - Mortgage rates: weekly granularity over-samples noise; quarterly mean suited for macro comparison

2. **Last-observation carry-forward** (metro prices):
   - End-of-quarter valuations capture market assessment at period boundary
   - Alternative (average): would smooth volatility but lose timing signals

3. **Left merge** (REIT/metro onto mortgage):
   - Mortgage rates rarely missing (continuous national series)
   - Ensures analysis sample = full REIT or metro sample, not reduced by mortgage data availability

4. **No imputation**:
   - Missing REIT fundamentals: rare; analysis can use complete-case or multiple imputation in M3
   - Missing prices: reflects real gaps in market coverage (acceptable for robustness checks)

---

## 7. Reproducibility Checklist

- [x] All raw data files present in `data/raw/`
- [x] Fetch scripts use **relative paths only** (via `config_paths.py`)
- [x] All scripts run without errors
- [x] Processed files saved to `data/processed/`
- [x] Final panel(s) saved to `data/final/`
- [x] Before/after row counts documented
- [x] Summary statistics printed to console
- [x] Data dictionary created (`data_dictionary.md`)

**To reproduce**:
```bash
python3 code/fetch_reit_data.py
python3 code/fetch_mortgage_data.py
python3 code/fetch_metro_prices_data.py
python3 code/merge_final_panel.py
```

---

## 8. Ethical Considerations & Data Limitations

### What we're losing:
- **Pre-2000 REIT history**: Analysis limited to 2000–2024 (24 years of data)
- **Sub-metro granularity**: Cannot analyze neighborhood-level price effects
- **Non-linear lags**: Quarterly panel cannot capture week-to-week rate shock propagation
- **Micro heterogeneity**: REITs aggregate to national level; cannot isolate regional sensitivity
- **Urban/Suburban classification**: Raw data does not include, would require external geocoding

### Ethical safeguards:
- No personally identifiable information (PII) in final datasets
- Zillow data public; REIT data from public filings
- Mortgage rates are published government data (FRED)
- Results will not identify or harm specific firms

---

## 9. Next Steps (M2/M3)

1. **M2 (Exploratory Analysis)**:
   - Visualize REIT/metro price trends vs. mortgage rates
   - Check for structural breaks (2008 financial crisis, 2020 pandemic)
   - Identify outliers and potential urban/suburban classification

2. **M3 (Econometric Models)**:
   - Panel regression: price/returns ~ mortgage rates + controls
   - Test differential sensitivity: REITs vs. metro price indices
   - Investigate lagged effects and interaction terms

---

**Report Generated**: February 24, 2026  
**Pipeline Version**: M1 (Data Pipeline)  
**Contact**: [Team members to be added to README.md]
