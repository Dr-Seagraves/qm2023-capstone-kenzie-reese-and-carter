[![Review Assignment Due Date](https://classroom.github.com/assets/deadline-readme-button-22041afd0340ce965d47ae6ef1cefeee28c7c493a6346c4f15d667ab976d596c.svg)](https://classroom.github.com/a/gp9US0IQ)
[![Open in Visual Studio Code](https://classroom.github.com/assets/open-in-vscode-2e0aaae1b6195c2367325f4f02e2d04e9abb55f0b24a779b69b11b9e10269abc.svg)](https://classroom.github.com/online_ide?assignment_repo_id=22634746&assignment_repo_type=AssignmentRepo)

# QM 2023 Capstone Project: U.S. Housing Prices & Mortgage Rates

**Course**: QM 2023 (Statistics II: Data Analytics)  
**Milestone**: M1 (Data Pipeline)  
**Due**: February 25, 2026

---

## Team Members & Roles

| Name | Roles | Responsibilities |
|------|-------|------------------|
| **Kenzie** | Lead Data Engineer, Analyst, Visualizer | Data pipeline architecture, REIT cleaning, analysis, visualization |
| **Reese** | Analyst, Visualizer | Research analysis, data interpretation, visualization |
| **Carter** | Analyst, Visualizer | Research analysis, data interpretation, visualization |

---

## Research Question

**How sensitive are regional home prices to mortgage rate changes, and do urban and suburban markets respond differently?**

### Context
Mortgage rates are the primary lever of monetary policy transmission to housing markets. Understanding the sensitivity of residential real estate values (and REIT returns) to rate changes informs both macroeconomic forecasting and portfolio management. This project tests whether the response differs systematically between urban (denser, higher-appreciation) and suburban (more price-sensitive) markets.

---

## Dataset Overview

### Primary Datasets

#### 1. REIT Returns & Fundamentals (2000–2024)
- **Source**: Compustat/CRSP merged panel (provided by course staff)
- **Coverage**: 27 unique REIT tickers, ~48,000 monthly observations
- **Key Variables**:
  - Returns: `usdret` (monthly USD return)
  - Valuation: `usdprc` (stock price), `market_equity`, `btm` (book-to-market), `beta`
  - Fundamentals: `assets`, `sales`, `net_income`, `roe` (return on equity)
- **Rationale**: REITs are the primary equity vehicle for real estate investment; returns reflect market expectations of future property values

#### 2. Metro Housing Price Index (Zillow ZHVI, 2000–2026)
- **Source**: Zillow Research (public data)
- **Coverage**: 894 U.S. metro areas
- **Key Variables**:
  - `price_index`: Zillow Home Value Index (mid-tier single family + condo)
  - `RegionName`, `StateName`: Metro identifiers
- **Rationale**: Captures market prices of actual residential properties; complements REIT-level analysis with granular geographic coverage

#### 3. National Mortgage Rates (1971–2026)
- **Source**: FRED (Board of Governors, series `MORTGAGE30US`)
- **Coverage**: Weekly 30-year fixed mortgage rate (%)
- **Key Variables**:
  - `MORTGAGE30US`: 30-year fixed rate (primary macro shock)
- **Rationale**: Mortgage affordability is the key transmission mechanism from policy rates to housing demand and prices

---

## Preliminary Hypotheses

### H1: Mortgage Rate Sensitivity (Sign & Magnitude)
**Regional home prices are negatively sensitive to mortgage rate increases.**
- When rates rise 100 bps, expected home price growth decelerates by 2–4 percentage points per year
- REIT returns exhibit similar (or larger) negative sensitivity due to leverage and discount rate effects
- This reflects the inverse relationship between discount rates and asset valuations

### H2: Differential Urban vs. Suburban Response
**Suburban markets are more price-sensitive to mortgage rate shocks than urban markets.**
- Suburban markets are more demand-elastic (elastic supply, price-sensitive buyer pool)
- Urban markets are supply-constrained (inelastic); prices driven more by income growth than financing costs
- Empirically: suburban ZHVI declines 0.5–1.5% per 100 bps rate increase; urban declines only 0.1–0.3%

### H3: Lagged & Non-Linear Effects
**The sensitivity of prices to rates exhibits lagged transmission and asymmetric adjustment.**
- Rate increases transmitted faster (6-12 months) than rate decreases (12-24 months)
- Large rate shocks (>200 bps) exhibit different elasticity than marginal changes
- REITs respond faster (market forward-looking) than metro prices (backward-looking appraisals)

---

## Final Datasets (M1 Deliverables)

| File | Rows | Columns | Key Variables |
|------|------|---------|---|
| `data/final/reit_mortgage_panel.csv` | 16,323 | 24 | ticker, date, usdret, usdprc, market_equity, MORTGAGE30US |
| `data/final/metro_mortgage_panel.csv` | 77,673 | 8 | RegionID, RegionName, date, price_index, MORTGAGE30US |
| `data/final/data_dictionary.md` | — | — | Variable definitions, units, sources |

**Panel Structure**: Long format (one row per entity-time observation), ready for panel regression analysis.

---

## How to Run the Pipeline

### Prerequisites
Ensure Python 3.8+ is installed with required packages:

```bash
pip install -r requirements.txt
```

### Step 1: Verify Project Structure
```bash
python3 code/config_paths.py
```
Expected output: Confirmation of all directory paths created and verified.

### Step 2: Clean Primary REIT Dataset
```bash
python3 code/fetch_reit_data.py
```
- Inputs: `data/raw/REIT_sample_2000_2024_All_Variables.csv`
- Outputs: `data/processed/reit_clean.csv` (48,019 rows)
- Time: ~5 seconds

### Step 3: Process Mortgage Rates to Quarterly
```bash
python3 code/fetch_mortgage_data.py
```
- Inputs: `data/raw/MORTGAGE30US.csv`
- Outputs: `data/processed/mortgage_quarterly.csv` (220 quarterly observations)
- Time: ~2 seconds

### Step 4: Reshape Metro Prices to Long Format & Quarterly
```bash
python3 code/fetch_metro_prices_data.py
```
- Inputs: `data/raw/Metro_zhvi_uc_sfrcondo_tier_0.33_0.67_sm_sa_month.csv`
- Outputs: `data/processed/metro_prices_quarterly.csv` (77,673 metro-quarters)
- Time: ~10 seconds

### Step 5: Merge into Final Analysis Panels
```bash
python3 code/merge_final_panel.py
```
- Inputs: All three processed datasets
- Outputs:
  - `data/final/reit_mortgage_panel.csv` (16,323 rows)
  - `data/final/metro_mortgage_panel.csv` (77,673 rows)
  - `data/final/data_dictionary.md`
- Time: ~5 seconds

### Full Pipeline (One Command)
```bash
python3 code/fetch_reit_data.py && \
python3 code/fetch_mortgage_data.py && \
python3 code/fetch_metro_prices_data.py && \
python3 code/merge_final_panel.py
```
**Total runtime**: ~25 seconds

---

## Project Structure

```
QM-2023-Capstone-Repo/
├── code/
│   ├── config_paths.py                      # Path management (DO NOT EDIT)
│   ├── fetch_reit_data.py                   # Fetch + clean REIT data
│   ├── fetch_mortgage_data.py               # Aggregate mortgage rates quarterly
│   ├── fetch_metro_prices_data.py           # Reshape metro ZHVI to long + quarterly
│   └── merge_final_panel.py                 # Merge into final analysis panels
├── data/
│   ├── raw/
│   │   ├── REIT_sample_2000_2024_All_Variables.csv
│   │   ├── MORTGAGE30US.csv
│   │   └── Metro_zhvi_uc_sfrcondo_tier_0.33_0.67_sm_sa_month.csv
│   ├── processed/
│   │   ├── reit_clean.csv
│   │   ├── mortgage_quarterly.csv
│   │   └── metro_prices_quarterly.csv
│   └── final/
│       ├── reit_mortgage_panel.csv         # ✅ Analysis-ready panel (REIT × quarters)
│       ├── metro_mortgage_panel.csv        # ✅ Analysis-ready panel (metros × quarters)
│       └── data_dictionary.md              # ✅ Variable definitions
├── results/
│   ├── figures/                             # (M2/M3 visualizations)
│   ├── tables/                              # (M2/M3 regression results)
│   └── reports/                             # (M2/M3 milestone memos)
├── tests/                                   # (Autograding suite)
├── README.md                                # ✅ This file
├── M1_data_quality_report.md                # ✅ Data cleaning & merge documentation
├── AI_AUDIT_APPENDIX.md                     # ✅ AI tool disclosure (Disclose-Verify-Critique)
└── requirements.txt                         # Python dependencies

```

---

## Key Design Decisions

### Quarterly Aggregation
- **Rationale**: Balances temporal granularity with noise reduction
- REITs file quarterly earnings; quarterly HPI removes seasonal noise
- Mortgage rates aggregated as **mean** (representative rate environment)
- Metro prices aggregated as **last observation** (end-of-period valuation)

### Left Merge Strategy
- REIT × mortgage: Left join retains all 16,323 REIT-quarters
- Metro × mortgage: Left join retains all 77,673 metro-quarters
- Ensures analysis sample = full original sample (not reduced by merge alignment)

### Separate Panels (REIT vs. Metro)
- REITs: Equity returns subject to discount rate effects (more direct macro sensitivity)
- Metros: Actual property prices sensitive to supply/demand fundamentals
- Enables **differential sensitivity tests** (H2): urban vs. suburban effect heterogeneity

---

## Data Quality Assurances

✅ **No hardcoded absolute paths** (all relative via `config_paths.py`)  
✅ **Before/after row counts** documented in fetch scripts  
✅ **Missing value handling** explicit (drop, carry-forward, mean imputation)  
✅ **Duplicate removal** verified (exact duplicates → 0)  
✅ **Date parsing** tested for timezone/format consistency  
✅ **Merge integrity** checked (no row loss, no duplicates)  
✅ **Reproducibility**: Full pipeline runnable in <1 minute  

---

## Documentation

- **M1_data_quality_report.md**: Detailed data sources, cleaning decisions, merge verification, and ethical considerations
- **AI_AUDIT_APPENDIX.md**: Transparent disclosure of AI tool usage (GitHub Copilot), following Disclose-Verify-Critique framework
- **data_dictionary.md**: Variable definitions, units, sources, and coverage

---

## Next Steps (M2 & M3)

### Milestone 2 (Exploratory Analysis)
- Visualize price trends vs. mortgage rates (time series plots)
- Identify structural breaks (2008 financial crisis, 2020 pandemic shock)
- Classify metros as urban vs. suburban (using population density, metro composition)
- Summary statistics by market type

### Milestone 3 (Econometric Analysis)
- Panel regression (Fixed Effects): price growth ~ Δ mortgage rates + controls
- Test differential sensitivity: urban vs. suburban interaction term
- Lag structure: examine 1–4 quarter lagged effects
- Robustness checks: alternative estimators (RE, GMM), alternative rate measures (15-yr, ARM)

---

## Contact & Questions

For questions about the data pipeline, research design, or reproducibility:
- **Email**: mit1334@utulsa.edu, rms1753@utulsa.edu, cbb6479@utulsa.edu

---

**Last Updated**: February 24, 2026  
**Status**: ✅ M1 Data Pipeline Complete  
**Submission**: Pending GitHub push and Blackboard upload
