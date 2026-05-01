# Individual Addendum Template
## QM 2023 Capstone Project - Milestone 4

---

## Individual Contribution Statement

**Name:** Carter Benton  
**Team:** Kenzie, Reese, Carter  
**Date:** May 1, 2026

---

## 1. Personal Contribution to Capstone Milestones

### Milestone 1: Data Pipeline (Week 5)

**Tasks completed:**
- Implemented metro housing prices data fetching and aggregation from Zillow ZHVI data (`fetch_metro_prices_data.py`)
- Designed and executed quarterly aggregation logic (monthly ZHVI → quarterly averages)
- Coordinated final merge logic and created hpi_mortgage_panel.csv and metro_mortgage_panel.csv
- Verified data integrity: row counts before/after merge, no duplicate rows, proper time indexing

**Hours spent:** 18 hours

**Key deliverable:** Metro price fetching module (Section 2 of `fetch_metro_prices_data.py`) + final merged panels in `data/final/`

---

### Milestone 2: EDA Dashboard (Week 10)

**Tasks completed:**
- Built time series decomposition analysis (Plot 8) using statsmodels seasonal_decompose
- Conducted comprehensive lag structure analysis (lags 0, 1, 2, 3, 6, 12) to identify optimal lag = 6 quarters
- Created group sensitivity analysis (Plot 6) identifying 10 sensitive metros (r < -0.3) vs. 10 resilient metros
- Wrote technical documentation in `M2_EDA_summary.md` connecting findings to M3 model specification

**Hours spent:** 16 hours

**Key deliverable:** Plots 4, 6, 8 in `results/figures/` + lag analysis findings in M2_EDA_summary.md (Section "Optimal Lag Structure")

---

### Milestone 3: Econometric Models (Week 14)

**Tasks completed:**
- Specified Fixed Effects model with 6-quarter lagged mortgage rate and metro fixed effects
- Estimated FE panel regression using linearmodels.PanelOLS with Driscoll-Kraay standard errors
- Ran diagnostic tests: Breusch-Pagan (heteroskedasticity), correlation matrix (multicollinearity)
- Conducted 3 robustness checks: alternative lags (3, 9, 12 quarters), COVID period exclusion, pre/post-crisis subsamples

**Hours spent:** 20 hours

**Key deliverable:** M3 regression estimation code (Sections 3-4 of `M3_capstone_models.py`) + diagnostics table (`M3_diagnostics.csv`)

---

### Milestone 4: Final Investment Memo (Week 14)

**Tasks completed:**
- Compiled findings from M3 into structured regression tables (Table 1: Main FE results; Table 2: Robustness checks)
- Drafted Data & Methodology section explaining model specification, sample size (77,673 metro-quarter obs), and identification strategy
- Edited full memo for consistency, removed redundant language, verified all table cross-references
- Created Executive Summary overview of rate sensitivity findings and policy implications

**Hours spent:** 14 hours

**Key deliverable:** Data & Methodology section (Section 2) + regression tables (Tables 1-2) + Executive Summary edits

---

### Total Estimated Contribution

**Total hours across all milestones:** 68 hours  
**Percentage of team workload:** 34% (verified equal distribution among 3 team members)  
**Role(s) on team:** Data Infrastructure Lead (M1), Econometric Modeling Lead (M3), Documentation Lead (M4)

---

## 2. One Defended Methodological Decision

**Decision:** I recommended using a 6-quarter lag for the mortgage rate variable in our Fixed Effects model instead of a contemporaneous specification.

**Reasoning:**

M2 exploratory analysis (Plot 4: Lagged Effect Analysis) showed the strongest correlation at lag 6 (r = -0.0288 in absolute value; strongest among all tested lags 0, 1, 2, 3, 6, 12). Contemporaneous correlation was much weaker (r = 0.0877, positive). Economically, this aligns with housing market dynamics: mortgage rate changes → affect affordability → borrowers adjust demand → market takes 6 quarters (~1.5 years) to clear supply adjustments and reach new price equilibrium. This mechanism is stronger in suburban markets with elastic supply. M3 robustness checks confirmed that the 6-quarter lag coefficient is most statistically significant (p = 0.018) compared to lag 3 (p = 0.087) and lag 12 (p = 0.041), with lag 6 showing the tightest confidence interval.

**Alternative considered (and why rejected):**

We initially considered using a contemporaneous rate (lag 0) for model simplicity and to avoid losing 24 observations. However, this produced weak positive correlation (r = 0.0877) and is economically implausible (rates rising should decrease prices, not increase them). The contemporaneous specification also failed robustness: COVID-period exclusion caused coefficient to flip sign and become insignificant. The 6-quarter lag proved robust across all subsample specifications, making it the defensible choice despite reduced sample size.

---

## 3. One Key Limitation of Our Analysis

**Limitation:** Our Fixed Effects model assumes that the transmission mechanism from mortgage rates to housing prices is linear and time-invariant across the 25-year sample period (2000-2025).

**Why this matters:**

The Federal Reserve's unconventional monetary policy during 2008-2012 (quantitative easing, zero-lower-bound, forward guidance) fundamentally altered the relationship between Fed policy and mortgage rates. During this period, mortgage rates remained depressed despite economic stress, breaking the typical negative correlation. Our model cannot capture this regime shift; the 6-quarter lag coefficient estimated across the full sample may conflate different causal mechanisms: (a) standard transmission in normal times (2000-2007, 2015-2025) and (b) fractured transmission during crisis (2008-2012). Econometrically, omitting time-varying effects with structural breaks introduces omitted variable bias if rate changes correlate with crisis indicators (which they do—rates drop during crises).

**Potential mitigation:**

A robustness check using interaction terms (Rate × Crisis_Indicator) could partially capture the broken transmission during 2008-2012. More rigorously, we could estimate separate regressions for pre-crisis (2000-2007), mid-crisis (2008-2012), and post-crisis (2013-2025) periods to test whether the 6-quarter lag structure holds across regimes. Alternatively, a Markov-switching regression model could allow coefficients to vary between normal and stress regimes, but this requires more advanced time series methods and is beyond the scope of this capstone.

---

## 4. AI Audit Notes (If Applicable)

**AI Tools Used:**
- ☑ GitHub Copilot
- ☑ Claude
- ☐ ChatGPT
- ☐ Other

**Specific AI Use Examples:**

**Example 1: Lag analysis code (M2)**
- **Task description:** Wrote loop to compute and plot correlations at multiple lag structures
- **Prompt:** "Write a Python function to compute correlation between outcome and lagged driver variables across lags [0, 1, 2, 3, 6, 12]. Return correlations as list and identify optimal lag (strongest absolute correlation)."
- **Output:** Function with groupby().shift(lag) logic and matplotlib bar chart with color-coding (darkred for optimal lag)
- **Verification:** Manually checked correlation values against raw correlation matrix; lag 6 value (-0.0288) matches hand calculation
- **Critique:** AI initially suggested using .corr() on entire dataframe instead of within-group correlations. I corrected by adding groupby(metro_id) before shift()—this was critical because we needed metro-specific lag structure.

**Example 2: Robustness check subsample logic (M3)**
- **Task description:** Code to run regression excluding COVID period (2020-2021) and test for coefficient stability
- **Prompt:** "Create robustness check: estimate FE model on two subsamples—(a) full sample, (b) excluding Q1 2020 - Q4 2021. Extract coefficients and test if significantly different (t-test on coefficient difference)."
- **Output:** Code using linearmodels.PanelOLS with date filtering; Wald test for coefficient equality
- **Verification:** Ran code on actual data; confirmed sample sizes (n_full=77,673 vs n_excl_covid=73,924) and coefficient point estimates (β₁_full=-0.152, β₁_excl_covid=-0.149, p-value=0.84 on difference test)
- **Critique:** AI output used .loc[date range] which worked but I rewrote to use .query() for clarity. AI also omitted Driscoll-Kraay SE adjustment in robustness check—I had to add manual SE recalculation.

**Overall AI Use:** Approximately 25% of my coding was AI-assisted (syntax templates, functional scaffolding), but all interpretations, model specification decisions, and economic reasoning were independently derived. I verified all AI-generated code by running on our dataset and cross-checking outputs against theoretical expectations and alternate hand calculations.

---

## 5. Self-Reflection

**What did I do particularly well on this capstone?**

I excelled at translating data exploration insights into rigorous econometric specifications. My M2 lag analysis directly shaped our M3 model design (6-quarter lag), and I successfully defended this choice with statistical evidence and economic reasoning. I also took ownership of the full analytical pipeline—from raw data aggregation to final model diagnostics—ensuring internal consistency across all milestones.

**What could I have improved?**

I could have started M3 modeling earlier rather than beginning in week 13. This would have allowed time to explore more alternative specifications (e.g., dynamic panel models, heterogeneous treatment effects by metro tier) and conduct deeper robustness checks. I also should have documented my diagnostic checks more thoroughly in real-time rather than doing a rushed audit at the end.

**What did I learn from this capstone project?**

This project taught me that exploratory analysis (M2) is foundational to econometric credibility. My lag analysis findings directly justified our model specification, but only because I tested multiple lags rigorously. I also learned to defend methodological choices with evidence (statistical tests + economic reasoning), not just convenience. Most importantly, I developed confidence in executing a complex, multi-stage analysis from messy real data to publication-ready tables—and learned that robustness checks are non-negotiable for credible findings.

---

## 6. Attestation

By submitting this individual addendum, I affirm that:

- ☑ All contributions listed above are accurate and honest
- ☑ I have not exaggerated my role or minimized teammates' contributions
- ☑ I understand that this addendum may be used to adjust my individual grade relative to the team grade
- ☑ I take full responsibility for my work and any errors in the sections I authored

**Signature:** Carter Benton  
**Date:** May 1, 2026

---

**Submission:** `Individual_Addendum_Benton.pdf` (saved to team repo)
