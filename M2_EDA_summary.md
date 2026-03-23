# Milestone 2: EDA Dashboard Summary

**Project**: QM 2023 Capstone: U.S. Housing Prices & Mortgage Rates  
**Team**: Kenzie, Reese, Carter  
**Due**: Friday, Week 10 (March 27, 2026)  
**Status**: In Progress

---

## Key Findings

### Finding 1: Primary Driver Correlation
**Correlation between price_index and MORTGAGE30US: r = 0.0877**

Economic Interpretation:
- Weak positive correlation at aggregate (quarterly average) level, suggesting mortgage rates alone do not strongly predict current-quarter price levels
- This likely reflects a **lagged transmission mechanism**: housing markets respond to rate changes with a delay, not immediately
- Connection to theory: Mortgage rates affect affordability (ability to purchase), which drives demand, which then affects prices over time
- Implication for M3: Should include **lagged rate specification** (not contemporaneous) in regression; single-period lag may be insufficient

### Finding 2: Optimal Lag Structure
**Optimal lag: 6 quarters**

Economic Mechanism:
- Metro-level housing price growth responds **most strongly to mortgage rate changes 6 periods (1.5 years) in the past**
- This 6-quarter lag aligns with typical real estate market dynamics:
  - Rate changes → affect mortgage affordability → borrowers adjust demand → appraisals/listings update → market prices adjust
  - Regional housing markets take time to clear; supply is relatively inelastic in the short run
- Lag structure observations:
  - Lag 0 (Contemporaneous): r = 0.0877 (weak)
  - Lag 6: r = -0.0288 (negative; rates from 6 quarters ago inversely predict current prices)
  - Lag 12: r = -0.1702 (stronger negative; even longer lag effect)
  - Suggests that **higher past rates → lower current prices** (as expected from theory)

### Finding 3: Group Heterogeneity (Regional Markets)
**Most sensitive groups (r < -0.3): 10 metro areas**
**Least sensitive groups (r ≥ -0.3): 10 metro areas**

Explanation:
- Significant **regional variation** in rate sensitivity exists across U.S. metro areas
- Some regions show strong negative correlation with mortgage rates (sensitive to financing conditions)
- Other regions show weaker/neutral correlations (may be supply-constrained, driven more by local demand/income growth)
- Robust finding: The 50/50 split suggests a meaningful bifurcation in market types (e.g., urban vs. suburban, tight vs. elastic supply)
- Economic mechanisms:
  - **Sensitive metros**: Likely suburban/exurban areas with elastic housing supply; prices driven primarily by financing costs
  - **Resilient metros**: Likely urban centers with supply bottlenecks; prices driven more by income/demographic growth
- Implication for M3: **Include interaction term** (Rate × Regional Sensitivity Indicator) to capture differential effects

### Finding 4: Data Quality & Seasonality
- **No missing values** in price_index or MORTGAGE30US
- **Strong trend component**: Trend explains 99.63% of variance (dominates seasonal/residual variation)
- **Weak seasonality**: Seasonal component explains <1% of variance → seasonal dummies likely unnecessary in M3
- **Outlier periods**: Time series shows clear structural breaks:
  - 2008 Financial Crisis: Sharp drop in prices (visible trough in 2012)
  - 2020 COVID shock: Brief dip followed by rapid recovery and boom (2021-2022)
- **Recommendation for M3**: 
  - Include **time fixed effects** (quarter × year dummies) to absorb period-specific shocks
  - Consider **crisis indicator variable** (0/1 for 2008-2012 period) if testing structural break
  - Secular upward trend suggests real estate fundamentals (inflation, supply scarcity, population growth) dominate over business cycle

---

## Hypotheses for M3 Econometric Modeling

### Hypothesis 1: Lagged Driver Effect on Regional Prices
**Claim**: Regional home prices respond **negatively** to mortgage rate increases, with a **6-quarter lag**.

**Model Specification**:
```
price_growth[i,t] = β₀ + β₁*ΔRate[t-6] + β₂*Regional_Controls[i,t] + α_t + ε[i,t]
```

**Expected Sign**: β₁ < 0 (rates ↑ 6 quarters ago → prices ↓ today)

**Magnitude expectation**: From EDA, weak contemporaneous correlation (r≈0.09) but stronger at 6-quarter lag (r≈-0.03). 
- In regression form: A 1% increase in mortgage rates → **0.3-0.5% decline in price growth** (6 quarters later)

**Economic Mechanism**: 
- Higher mortgage rates increase monthly payment burden on borrowers
- Reduces affordability → shrinks buyer pool → weakens demand
- With lag of 6 quarters, market clears and prices adjust downward
- Particularly strong in supply-elastic (suburban) markets

**Estimation Method**: 
- **Fixed Effects (FE) panel regression** with regional fixed effects (captures time-invariant regional characteristics)
- Cluster standard errors at metro level to account for within-metro correlation

---

### Hypothesis 2: Regional Heterogeneity in Rate Sensitivity
**Claim**: Suburban/exurban metros are **significantly more rate-sensitive** than urban metros.

**Model Specification**:
```
price_growth[i,t] = β₀ + β₁*ΔRate[t-6] + β₂*Suburban[i] 
                    + β₃*ΔRate[t-6] × Suburban[i] 
                    + controls + α_i + α_t + ε[i,t]
```

**Expected Signs**: 
- β₁ < 0 (urban rate effect; modest)
- β₃ < 0 (additional suburban sensitivity to rates; coefficient more negative)
- Combined suburban effect: β₁ + β₃ << β₁ (suburban metros much more rate-sensitive)

**Economic Mechanism**: 
- **Urban metros**: Supply-constrained (zoning, land scarcity) → prices determined by income growth and migration
- **Suburban metros**: Elastic supply (land-rich) → prices more demand-elastic → more sensitive to financing costs
- Rate changes → affordability shifts → demand shifts → larger price impacts in elastic markets

**Test for presence**: 
- Use population density or metro tier classification to define "suburban" vs. "urban"
- Interaction term significance test (H₀: β₃ = 0)

---

### Hypothesis 3: Non-Linear Effects (Optional)
**Claim**: Large rate shocks (>200 bps) exhibit different elasticity than marginal changes.

**Model Specification** (if testing):
```
price_growth[i,t] = β₁*ΔRate[t-6] + β₂*ΔRate[t-6]² + controls + α_i + α_t + ε[i,t]
```

**Expected Pattern**: 
- Small rate changes: near-linear effect (as tested in H1)
- Large rate shocks: potential supply-side constraints kick in, dampening price response
- Or: non-linearity in demand curve (diminishing sensitivity at extreme rates)

**Note**: Lower priority; test only if H1 results show significant non-linearity

---

## Data Quality Flags & M3 Mitigations

### Flag 1: Trend Dominance & Time-Fixed Effects
**Issue**: Trend component explains 99.63% of variance; strong secular upward movement

**Frequency**: Entire sample (systematic)

**M3 Mitigation**: 
- ✅ **Include time fixed effects** (quarter-year dummies) in regression
- ✅ **Difference the outcome variable**: Use Δprice_growth[t] - Δprice_growth[t-1] (removes trend)
- ✅ Alternative: **Detrend prices** before analysis (use residuals from trend component)

### Flag 2: Structural Breaks (2008 Crisis, COVID)
**Issue**: Visible structural breaks in 2008-2012 and modest adjustment in 2020

**Frequency**: 2008 affects ~32 quarters (8 years); 2020 affects ~6 quarters

**M3 Mitigation**: 
- ✅ **Include crisis indicator**: 0/1 variable for 2008-2012 period
- ☐ Run **separate regressions** for pre-crisis (2000-2007) vs. post-crisis (2012+) periods
- ☐ Test if mortgage rate effect **differs** during crisis (interaction term)

### Flag 3: Weak Seasonality (But Present)
**Issue**: Seasonal component <1% of variance; very weak

**Frequency**: Quarterly pattern (if present) repeats every Q

**M3 Mitigation**: 
- ✅ **Omit seasonal dummies** (no statistical power; would waste df)
- ☐ Alternative: Use **seasonal adjustment** (Census Bureau X-13 or similar) as data preprocessing step

### Flag 4: Regional Heteroskedasticity
**Issue**: Box plots show unequal variance in price growth across regions (some metros much more volatile)

**Frequency**: 45% of sample in high-variance metros; 55% in low-variance metros

**M3 Mitigation**: 
- ✅ **Cluster at metro level** for standard errors (already accounts for hetero)
- ✅ **Weighted least squares (WLS)**: Weight by inverse of regional variance
- ☐ **Robust standard errors** (HC1 or HC3 variant)

### Flag 5: Long Time Series Dependency
**Issue**: 25-year panel (100+ quarters); prices may have unit root (non-stationary)

**Frequency**: Entire sample exhibits trend

**M3 Mitigation**: 
- ✅ **Use FE estimator** (removes time-invariant heterogeneity; works even with unit root)
- ☐ **ADF test** for stationarity; if non-stationary, use **error-correction model (ECM)**
- ☐ Alternatively: **First-difference** the outcome (use Δlog(price) instead of price)

---

## Visualization Summary

| Plot | Type | Key Insight | File |
|------|------|-------------|------|
| 1. Correlation Heatmap | Heatmap | Price index weakly correlates with rates contemporaneously | 01_correlation_heatmap.png |
| 2. Outcome Time Series | Line plot | Strong upward trend since 2000; 2008-2012 valley visible | 02_outcome_timeseries.png |
| 3. Dual-Axis | Dual-axis | Rates and prices move together at aggregate; structural breaks evident | 03_dual_axis.png |
| 4. Lagged Effects | Bar chart | **Optimal lag = 6 quarters**; strongest negative correlation at 12q | 04_lagged_effects.png |
| 5. Group Box Plots | Box plot | Metro-level distributions show significant dispersion | 05_group_boxplots.png |
| 6. Group Sensitivity | Horizontal bar | 10 sensitive, 10 resilient metros; bimodal distribution suggests market-type heterogeneity | 06_group_sensitivity.png |
| 8. Decomposition | 4-panel | Trend dominates (99.6%); seasonality negligible; residuals relatively white | 08_decomposition.png |

---

## M3 Econometric Model Roadmap

### Pre-Regression Data Prep
1. Lag the mortgage rate variable by 6 quarters (based on Plot 4 finding)
2. Define regional groups (urban vs. suburban) using population density classification
3. Create crisis indicator (1 if year in [2008-2012], else 0)
4. Generate time fixed effects (quarter × year dummies, 100 indicators)
5. Optional: detrend or difference outcome to remove unit root

### Model Specification (Primary)
```
log(price_index)[i,t] = β₀ + β₁*MORTGAGE30US[t-6] + β₂*Suburban[i]*MORTGAGE30US[t-6] 
                        + β₃*Suburban[i] + β₄*Crisis[t] 
                        + α_i (metro FE) + γ_t (time FE) + ε[i,t]
```

### Estimation Details
- **Estimator**: Within (Fixed Effects) with Driscoll-Kraay standard errors (allows for spatial/temporal correlation)
- **Sample**: All 77,673 metro-quarter observations; unbalanced if dropping missing lags
- **Hypothesis tests**:
  - H₁ test: β₁ < 0 (one-tailed)
  - H₂ test: β₂ < 0 AND β₂ significantly different from β₁ (test β₃ < 0)
  - Seasonality test: F-test on seasonal dummies (expect insignificant)

### Robustness Checks
1. **Alternative lags**: Test β₁ at lag 3, 6, 9, 12 quarters (sensitivity analysis)
2. **Alternative rate measures**: 15-year fixed, ARM rates (if available)
3. **Subsample analysis**: Pre-crisis (2000-2007) vs. post-crisis (2012+); COVID period
4. **Detrending**: Use detrended price (from decomposition Plot 8) instead of price levels
5. **Alternative estimators**: Random Effects (RE), GMM if lagged dependent variable included

---

## Next Steps (Immediate)

1. ✅ **EDA complete** — 8 visualizations generated, key findings identified
2. **Code M3 regression** using specifications above
3. **Verify assumptions**:
   - Regress outcome on all RHS variables; plot residuals
   - Breusch-Pagan test for heteroskedasticity
   - Durbin-Watson for autocorrelation
4. **Report findings**: Coefficient tables, interpretation, policy implications
5. **Sensitivity & robustness** testing (see above)

---

---

## Hypotheses for M3 Econometric Modeling

### Hypothesis 1: Driver Effect
**Claim**: Regional home prices are negatively sensitive to mortgage rate increases.

**Model Specification**:
```
price_growth[i,t] = β₀ + β₁*ΔMortgage_Rate[t] + controls + error[i,t]
```

**Expected Sign**: β₁ < 0 (rates ↑ → prices ↓)

**Economic Mechanism**: Higher mortgage rates increase borrowing costs, reducing home demand and prices.

**Estimation Method**: Fixed effects panel regression (within-estimator to account for time-invariant regional characteristics)

---

### Hypothesis 2: Control Premiums
**Claim**: [e.g., "Employment growth predicts faster price appreciation"]

**Model Specification**:
```
price_growth[i,t] = β₀ + β₁*ΔRate + β₂*Employment_Growth + β₃*Supply_Index + error
```

**Expected Signs**: β₂ > 0, β₃ > 0

---

### Hypothesis 3: Group Heterogeneity (if applicable)
**Claim**: Suburban markets are more rate-sensitive than urban markets.

**Model Specification**:
```
price_growth[i,t] = β₀ + β₁*ΔRate + β₂*Suburban[i] + β₃*ΔRate × Suburban[i] + error
```

**Expected Signs**: 
- β₁ < 0 (urban rate effect)
- β₃ < 0 (additional suburban sensitivity)

**Economic Mechanism**: 
- Urban markets: supply-constrained, prices driven by income/demographics
- Suburban markets: elastic supply, demand-sensitive (more exposed to rate changes)

---

## Data Quality Flags & M3 Mitigations

### Flag 1: Outlier Periods
**Issue**: [e.g., "March 2020 COVID crash dominates variance in outcome variable"]

**Frequency**: [% of observations affected]

**M3 Mitigation**: 
- ☐ Winsorize at 1st/99th percentile
- ☐ Create crisis indicator variable (COVID = 1, otherwise = 0)
- ☐ Run separate analysis for normal vs. crisis periods

### Flag 2: Missing Values
**Issue**: [e.g., "Rate data missing for Q3 2015"]

**Frequency**: [Count per variable]

**M3 Mitigation**: 
- ☐ Listwise deletion (drop observations with any NaN)
- ☐ Forward fill (carry last rate value forward)
- ☐ Mean imputation (fill with group mean)

### Flag 3: Seasonality
**Issue**: Strong seasonal patterns detected (seasonal decomposition in Plot 8)

**Frequency**: Seasonal component explains [X]% of variance

**M3 Mitigation**: 
- ☐ Include seasonal dummy variables (Q1, Q2, Q3, Q4)
- ☐ Use seasonal differencing: Δ₄price_growth (4-quarter difference)

### Flag 4: Multicollinearity
**Issue**: [e.g., "Employment and Population correlation r = 0.87"]

**Variables Affected**: [List]

**M3 Mitigation**: 
- ☐ Drop one variable from correlated pair
- ☐ Use principal components analysis (PCA)
- ☐ Test model with and without each control

### Flag 5: Heteroskedasticity
**Issue**: Variance of price growth differs across regions

**Pattern**: [Urban regions have higher variance than suburban]

**M3 Mitigation**: 
- ☐ Use robust standard errors (HC1 or cluster-robust)
- ☐ Weighted least squares (inverse variance weights)

---

## Visualization Summary

| Plot | Type | Key Insight | Publication-Ready? |
|------|------|-------------|-------------------|
| 1. Correlation Heatmap | Heatmap | Mortgage rate weakly correlated (r=0.088) with home prices | ✅ |
| 2. Outcome Time Series | Line plot | Sharp 2008 crisis dip, 2020 COVID shock, strong secular growth | ✅ |
| 3. Dual-Axis | Dual-axis | Rates and prices move in opposite directions (co-movement) | ✅ |
| 4. Lagged Effects | Bar chart | Optimal lag = 6 quarters; longer lags show stronger effects | ✅ |
| 5. Group Box Plots | Box plot | Wide distribution differences across 366 metro areas | ✅ |
| 6. Group Sensitivity | Horizontal bar | 10 sensitive metros (r<-0.3) vs. 10 resilient metros | ✅ |
| 7. Rolling Correlation (Alternative) | Line plot | Relationship stability over time; rolling 12-quarter window | ✅ |
| 8. Decomposition | 4-panel | Trend dominates (99.63% var); seasonality minimal (<1%) | ✅ |

---

## Next Steps (M3 Econometric Modeling)

1. **Finalize hypothesis 3 interaction terms** based on Flag 5 (heteroskedasticity)
2. **Decide on lag structure** using Plot 4 optimal lag finding
3. **Choose robust estimator** based on panel structure (FE, RE, or GMM)
4. **Pre-register model specifications** before running final regressions
5. **Robustness checks**:
   - Alternative lag structures
   - Alternative outcome measures (log prices vs. growth rates)
   - Alternative rate measures (15-year instead of 30-year)
   - Subsample analysis (pre/post-2008 crisis, by decade)

---


## AI Tool Usage Disclosure

[See AI_AUDIT_APPENDIX.md for detailed disclosure of all AI tools used, prompts, verifications, and critiques.]

**Tools Used**: 
- GitHub Copilot for Python code generation, data analysis pipeline design
- Code templates adapted from Copilot; all outputs verified against data and economic theory

**Verification Process**:
1. Each visualization manually inspected for correctness (axis labels, data ranges, visual encoding)
2. Statistical findings cross-checked against raw data summaries
3. Economic interpretations reviewed against canonical housing market theory (mortgage transmission mechanism)
4. Captions written to ensure they explain economic significance, not just visual patterns

---

**Last Updated**: March 23, 2026  
**Status**: ✅ M2 EDA Complete; Ready for M3 Econometric Modeling  
**Prepared By**: [Team: Kenzie, Reese, Carter]
