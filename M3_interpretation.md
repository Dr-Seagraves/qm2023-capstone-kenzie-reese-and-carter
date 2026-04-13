# Milestone 3 Interpretation Memo

## Project Context
Research question: How sensitive are regional home prices to mortgage rate changes, and do high-volatility markets respond differently after the 2022 rate-hike cycle?

Data used: [data/final/metro_mortgage_panel.csv](data/final/metro_mortgage_panel.csv) with metro-level panel observations and mortgage rates.

## Model A Headline (Fixed Effects)
Headline result: A 1 percentage point increase in lagged mortgage rates, scaled by metro-specific exposure, is associated with a 0.1077 percentage point decline in quarterly home price growth (beta = -0.1077, p < 0.001).

Interpretation in economic units:
- At median exposure (1.486), a 1 pp mortgage increase implies about a 0.160 pp decline in quarterly price growth.
- At 75th percentile exposure (1.883), a 1 pp mortgage increase implies about a 0.203 pp decline in quarterly price growth.
- Over the observed first-2022 to last-2023 mortgage increase (about 3.48 pp), the implied reduction is about 0.56 pp (median exposure) to 0.71 pp (high exposure) in quarterly growth.

Model A also shows persistence in housing growth: lagged price growth coefficient is 0.5596 (p < 0.001), indicating momentum in metro housing dynamics.

## Economic Interpretation and Causal Channels
The negative mortgage coefficient is economically sensible and consistent with housing finance theory:

1. Affordability channel
Higher mortgage rates reduce borrower purchasing power, lowering effective demand and slowing price growth.

2. User-cost channel
Higher financing costs raise the user cost of housing, reducing willingness to pay and compressing valuations.

3. Credit and underwriting channel
Rate increases tighten debt-service constraints and can reduce marginal buyer qualification, especially in high-volatility metros.

## Model B Summary (Difference-in-Differences)
Model B estimate: treated_post = -0.4000 (SE = 0.0283, p < 0.001).

Interpretation: high-exposure metros experienced about 0.40 percentage points lower quarterly price growth after the 2022 hike period, relative to lower-exposure metros, conditional on entity and time fixed effects.

Key takeaway: both Model A and Model B point to economically meaningful negative sensitivity of price growth to mortgage tightening.

Pre-trends visual check: [results/figures/M3_did_pretrends.png](results/figures/M3_did_pretrends.png) shows treated and control group average growth paths before the policy cutoff.

## Diagnostics (Assumptions, Implications, and Fixes)
Outputs referenced from [results/tables/M3_diagnostics.csv](results/tables/M3_diagnostics.csv), [results/figures/M3_residuals_vs_fitted.png](results/figures/M3_residuals_vs_fitted.png), and [results/figures/M3_qq_plot.png](results/figures/M3_qq_plot.png).

1. Heteroskedasticity (Breusch-Pagan)
- LM p-value = 1.99e-53, F p-value = 1.64e-53.
- Interpretation: strong evidence of heteroskedasticity.
- Fix applied: clustered standard errors by entity are used in final reporting.

2. Multicollinearity (VIF)
- VIF(mortgage_exposure_lag3) = 1.01.
- VIF(price_growth_lag1) = 1.01.
- Interpretation: multicollinearity is negligible; no variable removal needed on VIF grounds.

3. Residual diagnostics
- Residual vs fitted and Q-Q plots were generated and reviewed.
- Interpretation: residual spread is acceptable for panel work, with non-perfect normality expected in macro-financial data.
- Inference remains based on clustered standard errors rather than normality assumptions.

## Robustness Checks
Results referenced from [results/tables/M3_robustness_lags.csv](results/tables/M3_robustness_lags.csv) and [results/tables/M3_robustness_checks.csv](results/tables/M3_robustness_checks.csv).

1. Clustered vs conventional SE
- Baseline coefficient unchanged (-0.1077), clustered SE is slightly larger (0.00642 vs 0.00578).
- Implication: significance is not an artifact of underestimated standard errors.

2. Alternative lag structures
- Lag 1 coefficient: -0.1476 (p < 0.001)
- Lag 2 coefficient: -0.1368 (p < 0.001)
- Lag 3 coefficient: -0.1077 (p < 0.001)
- Implication: sign and significance are stable across lags; mortgage tightening effect is robust to lag choice.

3. Excluding outlier period (2020-03 to 2020-05)
- Baseline: -0.1077
- Excluding outliers: -0.1065
- Implication: core result is not driven by COVID shock quarters.

4. Placebo DiD pre-trend test
- Placebo treated_post coefficient: +0.3605 (p < 0.001)
- Implication: pre-trends differ between treated and control groups, so DiD causal interpretation should be treated cautiously.

## Explicit Limitations Paragraph for Main Report
Although the DiD coefficient is statistically strong, the pre-trends evidence indicates that treated and control metros were not evolving in parallel before treatment, which weakens strict causal interpretation for Model B. In addition, treatment status is based on a constructed exposure metric rather than an externally assigned policy treatment, and the model omits some local demand/supply controls (for example, inventory, migration, and employment shocks). These limitations mean the DiD result is best interpreted as directional and suggestive, while Model A fixed-effects estimates with clustered standard errors remain the primary empirical result.

## Caveats and Limitations
1. Parallel trends concern in DiD
The significant placebo estimate suggests that treated and control metros were already evolving differently before the policy period. This weakens strict causal interpretation of Model B.

2. Omitted variables
The panel does not directly include local labor market, inventory, or migration controls in this script. Some remaining confounding is possible.

3. Constructed treatment definition
Treatment is based on pre-period volatility exposure, which is defensible but not a policy-assigned treatment.

4. External validity
Findings are strongest for this metro sample and time window; extrapolation to other periods should be cautious.

## Bottom Line
Model A provides a robust, statistically strong negative relationship between mortgage tightening and metro price growth under entity and time fixed effects with clustered standard errors. Model B supports the same direction but should be interpreted with caution due to placebo evidence against strict parallel trends.
