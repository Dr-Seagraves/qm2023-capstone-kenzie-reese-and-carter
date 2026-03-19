# M2 EDA Summary

## Key Findings

- Negative outcome-driver correlation: national quarterly home price growth is negatively correlated with 30-year mortgage rate (r ≈ -0.176), consistent with economic theory that higher financing cost dampens demand and price appreciation.
- Optimal lag: strongest price-growth relationship to mortgage rate occurs at 2-quarter lag (r ≈ -0.229), implying mortgage rate changes feed into housing prices with a 6-month adjustment window, useful for M3 lag structure.
- Group heterogeneity: state-level sensitivity shows strong negative responses in Idaho (r ≈ -0.431), South Dakota (r ≈ -0.387), Utah (r ≈ -0.379) versus weak positive or neutral in NY/NJ/CT. This suggests regional leverage/market structure matters.
- Control pattern: SizeRank has modest negative correlation with growth (bigger metros are lower rank and show slightly higher growth), highlighting scale effects.
- Outlier & event signals: plot time series indicated COVID-2020 and 2022 rate-hike volatility spikes, plus persistent rising trend 2020-2024 in price index.

## Hypotheses for M3

1. Driver effect:
   - Hypothesis: Higher 30-year mortgage rates reduce quarterly home price growth in metro areas.
   - Spec: `price_index_growth_{i,t} = beta_0 + beta_1*MORTGAGE30US_{i,t-lag} + ... + error`.
   - Expected sign: beta_1 < 0.
   - Mechanism: borrowing cost rise depresses demand and loosens affordability.

2. Control effect:
   - Hypothesis: Larger metros (lower SizeRank) experience stronger price growth even after controlling for rates.
   - Spec: add `SizeRank` (or size quartiles) as control; expect negative coefficient on SizeRank.
   - Expected sign: beta_size < 0.

3. Group heterogeneity:
   - Hypothesis: rate sensitivity differs by state; low supply states (e.g., ID, UT) have stronger negative mortgage-rate effect than high-regulation states (NY, NJ, CT).
   - Spec: include `State * MORTGAGE30US` interaction or state fixed effects with slopes.

## Data Quality Flags and M3 Mitigations

- Missing values: quarterly growth is NA for first observation within each metro; use panel-level lagged differences and drop first row per group, no systemic missingness.
- Outliers: COVID 2020 and 2022 spike/decline periods visible; include crisis dummy or robust regression to mitigate.
- Heteroskedasticity: variance across states/metro groups differs in box plots; use cluster-robust SEs or hierarchical model in M3.
- Multicollinearity: mortgage rate and lagged mortgage rate are highly correlated, so avoid using multiple adjacent lags in same basic model, or use penalized regression / VIF checks.

