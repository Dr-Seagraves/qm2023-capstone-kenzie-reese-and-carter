# AI Audit Appendix

**Disclosure-Verify-Critique Framework Compliance**

Required for all milestones. Document AI use with "Disclose, Verify, Critique":


## AI Tools Used
- GitHub Copilot (VS Code extension)
- GitHub Copilot Chat (VS Code)

**Models referenced across milestones**:
- Claude Haiku 4.5 (earlier milestone support)
- GPT-5.3-Codex (Milestone 3 support)


## Per Task

### Task 1: REIT Data Pipeline (fetch_reit_data.py)
- **Task:** Generate Python script to fetch, clean, and aggregate REIT data from raw CSV
- **Prompt:** "Retrieve the REIT Master Panel data set as the primary data set, and fet anything you need by default"
- **AI Output:** Modular fetch + clean function with docstrings and error handling (~50 LOC)
- **Verification:** Ran against `data/raw/REIT_sample_2000_2024_All_Variables.csv` → 48,019 rows processed; saved to `data/processed/reit_clean.csv`
- **Critique:** Code structure strong; required human fix for pandas 3.0 deprecation ('Q' → 'QE-DEC')

### Task 2: Mortgage Data Pipeline (fetch_mortgage_data.py)
- **Task:** Generate script for quarterly aggregation of FRED 30-year mortgage rates
- **Prompt:** "This is the instructions for mileston 1 of my capstone project. The question that my teammates and I are trying to anser are, "U.S. Housing Prices & Mortgage Rates
Research Question: How sensitive are regional home prices to mortgage rate changes, and do urban and suburban markets respond differently?" Please help with the things we need to do for the milestone. Let me know what data I need to provide for you."
- **AI Output:** Quarterly resampling logic with proper frequency alignment (~60 LOC)
- **Verification:** Ran against `data/raw/MORTGAGE30US.csv` → 220 quarterly aggregates; saved to `data/processed/mortgage_quarterly.csv`
- **Critique:** Pandas version assumptions failed; updated to 'QE-DEC' for modern pandas compatibility

### Task 3: Metro Housing Prices Pipeline (fetch_metro_prices_data.py)
- **Task:** Generate script to reshape Zillow ZHVI data from wide to long format and aggregate quarterly
- **Prompt:** "This is the instructions for mileston 1 of my capstone project. The question that my teammates and I are trying to anser are, "U.S. Housing Prices & Mortgage Rates
Research Question: How sensitive are regional home prices to mortgage rate changes, and do urban and suburban markets respond differently?" Please help with the things we need to do for the milestone. Let me know what data I need to provide for you."
- **AI Output:** Long formatting + aggregation logic with flexible column detection (~70 LOC)
- **Verification:** Ran against metro ZHVI CSV → 77,673 metro-quarter observations; saved to `data/processed/metro_prices_quarterly.csv`
- **Critique:** Required human debugging for date parsing edge cases; added error handling

### Task 4: Final Panel Merge (merge_final_panel.py)
- **Task:** Generate script to merge REIT, mortgage rates, and metro prices into separate analysis panels
- **Prompt:** "This is the instructions for mileston 1 of my capstone project. The question that my teammates and I are trying to anser are, "U.S. Housing Prices & Mortgage Rates
Research Question: How sensitive are regional home prices to mortgage rate changes, and do urban and suburban markets respond differently?" Please help with the things we need to do for the milestone. Let me know what data I need to provide for you."
- **AI Output:** Multi-dataset merge strategy with validation (~160 LOC)
- **Verification:** Ran all three merges; checked final dimensions → Two panels created successfully with no row loss
- **Critique:** Merge on str/datetime type mismatch required explicit `pd.to_datetime()` conversion; human added verification checks for duplicates

### Task 5: Documentation (M1_data_quality_report.md, README.md)
- **Task:** Generate data quality report table format and update README with team roles
- **Prompt:** "This is the instructions for mileston 1 of my capstone project. The question that my teammates and I are trying to anser are, "U.S. Housing Prices & Mortgage Rates
Research Question: How sensitive are regional home prices to mortgage rate changes, and do urban and suburban markets respond differently?" Please help with the things we need to do for the milestone. Let me know what data I need to provide for you." AND "Please run them and ensure everything is going to the right folders."
- **AI Output:** Documentation templates and role descriptions
- **Verification:** Human reviewed for accuracy and specificity; edited for domain relevance
- **Critique:** Structure solid; required fact-checking against actual data dimensions and team roles

### Task 6: Ensuring correct time frames and series (merge_final_panel.py)
- **Task:** Add FRED fetch, merge scripts and detect date/identifier columns
- **Prompt:** "Quarterly and use the mortgage rate series listed."
- **AI Output:** Fixed data column names, ensured dates were correct.
- **Verification:** Human reviewed for accuracy and specificity
- **Critique:** Structure solid; required fact-checking against actual data dimensions and team roles

### Task 7: Ensuring correct time frames and series (merge_final_panel.py)
- **Task:** Check new datasets, reprocess them, complete remaining documentation
- **Prompt:** "I have now added in the data sets we will that we are using. Go back through the instructions and do anything else you need to do for the milestone. Make sure everything is and/or was going to the correct folder."
- **AI Output:** Ensured everything was correct.
- **Verification:** Human reviewed for accuracy and specificity
- **Critique:** NA

### Task 8: Edits to the the ReadME.md file
- **Task:** Update the files with team names and roles.
- **Prompt:** "On the README.md where it lists team members and roles, put "Reese" on a different line and list her as analyst and visualizer, same with carter. List Kenzie as lead data engineer, analyst and visualizer. Update the AI_AUDIT_APPENDIX if needed"
- **AI Output:** Updated the team names and roles
- **Verification:** Human reviewed for accuracy and specificity
- **Critique:** NA

### Task 9: Make updates to the AI_AUDIT_APPENDIX.md
- **Task:** Change the format of the AI Audit Appendix
- **Prompt:** "Make the AI_AUDIT_APPENDIX.md be formatted to look like the pasted image. The current one is too complex and I need it to look like the photo. I can add the exact AI prompts I used if needed, or if you can pull them from the chat"
- **AI Output:** Changed the format to match, and make it simplier to read
- **Verification:** Human reviewed for accuracy and specificity
- **Critique:** NA

### Task 10: Milestone 3 model script generation (M3_capstone_models.py)
- **Task:** Convert Milestone 3 instructions into executable Python code with required models and outputs
- **Prompt:** "convert this to python code"
- **AI Output:** Created `M3_capstone_models.py` implementing:
	- Model A Fixed Effects (PanelOLS with entity and time effects)
	- Model B Difference-in-Differences
	- Diagnostics: Breusch-Pagan, VIF, residual plots
	- Robustness checks: clustered vs standard SE, alternative lags, outlier exclusion, placebo DiD
	- Automated output saves to `results/tables/` and `results/figures/`
- **Verification:** Ran the script from scratch and confirmed successful completion and output files.
- **Critique:** First draft used high-dimensional dummy OLS and timed out; revised to `linearmodels.PanelOLS` for speed and stable execution.

### Task 11: Rubric alignment upgrade for Milestone 3 outputs
- **Task:** Ensure Milestone 3 deliverables match rubric formatting and content requirements
- **Prompt:** "make sure milestone 3 fits this rubric and make an AI audit for milestone 3 as well"
- **AI Output:** Updated regression table generation to include side-by-side model columns with coefficient, standard error, t-stat, p-value, significance stars, and notes rows (Entity FE, Time FE, Clustered SE, N, R2).
- **Verification:** Re-ran script and confirmed updated table in `results/tables/M3_regression_table.csv`.
- **Critique:** Required human review of whether the DiD design fully supports causal interpretation; AI cannot guarantee identification assumptions from code alone.

### Task 12: Milestone 3 interpretation and rubric crosswalk documentation
- **Task:** Draft required interpretation memo and explicit rubric checklist evidence
- **Prompt:** "make sure milestone 3 fits this rubric and make an AI audit for milestone 3 as well"
- **AI Output:** Created:
	- `M3_interpretation.md` with model findings, diagnostics interpretation, robustness implications, and caveats
	- `M3_rubric_alignment.md` mapping deliverables to rubric categories and evidence files
- **Verification:** Human reviewed numerical values against generated model outputs in `results/tables/`.
- **Critique:** Placebo DiD result was significant in pre-period; memo explicitly documents this limitation instead of overstating causal confidence.

### Task 13: DiD pre-trends figure and explicit limitations paragraph
- **Task:** Keep DiD model and strengthen reporting with pre-trends visualization and direct limitations language in the report text
- **Prompt:** "2."
- **AI Output:** Updated `M3_capstone_models.py` to produce `results/figures/M3_did_pretrends.png` and updated `M3_interpretation.md` with a dedicated explicit limitations paragraph referencing pre-trends concerns.
- **Verification:** Re-ran `M3_capstone_models.py` successfully and confirmed new figure output plus updated interpretation text.
- **Critique:** Visual pre-trends checks improve transparency but do not fully resolve identification concerns; formal event-study style checks could be added in future revisions.

### Task 14: Milestone 3 machine-learning benchmark integration
- **Task:** Extend Milestone 3 with predictive machine-learning models while keeping FE/DiD econometric outputs intact.
- **Prompt:** "use machine learning for milestone 3"
- **AI Output:** Updated `M3_capstone_models.py` to add a held-out time split ML workflow using:
	- Linear Regression
	- Random Forest Regressor
	- Gradient Boosting Regressor
	- Evaluation metrics: RMSE, MAE, R2
	- Feature-importance export for best model
	- Prediction figure: actual vs predicted holdout averages
	- New outputs:
	  - `results/tables/M3_ml_metrics.csv`
	  - `results/tables/M3_ml_feature_importance.csv`
	  - `results/figures/M3_ml_actual_vs_predicted.png`
- **Verification:** Re-ran `M3_capstone_models.py`; confirmed successful run and presence of all new ML output files with populated metrics.
- **Critique:** Holdout test gives one split only; results can vary with split date, so additional temporal validation is needed for stronger model comparison.

### Task 15: Expanding-window time-series cross-validation for ML
- **Task:** Improve ML evaluation reliability by adding rolling/expanding-window cross-validation over dates.
- **Prompt:** "1."
- **AI Output:** Updated `M3_capstone_models.py` with expanding-window CV logic and per-fold/per-model tracking. Added new outputs:
	- `results/tables/M3_ml_cv_results.csv` (fold-level RMSE/MAE/R2 by model)
	- `results/tables/M3_ml_cv_summary.csv` (mean/std metrics and rank by CV RMSE)
	- Best-model selection now based on CV summary before feature-importance and holdout plot reporting.
- **Verification:** Re-ran `M3_capstone_models.py`; script completed successfully and both CV files were generated with multiple folds and all models represented.
- **Critique:** CV improves temporal robustness, but this is still not a causal design; predictive performance should complement, not replace, FE/DiD interpretation.

## Summary
**Total AI use**: 15 documented primary tasks across Milestones 1-3  
**Primary use cases**: Data ETL scripting, econometric model scaffolding, diagnostics/robustness workflow setup, machine-learning benchmarking, time-series cross-validation, documentation templates, formatting, and QA checklists
**Verification method**: Code execution from scratch, output file checks, coefficient/diagnostic spot checks, ML metric/CV table validation, and team human review

**Responsibility**: All code is tested and debugged by human team. AI provides efficient templates; humans ensure correctness, compatibility, and domain appropriateness.

---

## Attestation

**Human Team** (Kenzie, Reese, Carter) certifies:
- ✅ All AI-generated code has been tested and validated
- ✅ All code modifications documented above
- ✅ No prompts designed to circumvent academic integrity policies
- ✅ Human judgment made all substantive decisions
- ✅ Final deliverables ready for grading

---

**Date**: April 20, 2026  
**Tool**: GitHub Copilot and GitHub Copilot Chat (GPT-5.3-Codex used for M3)  
**Status**: ✅ Compliant
