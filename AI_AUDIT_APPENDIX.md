# AI Audit Appendix

**Disclosure-Verify-Critique Framework Compliance**

Required for all milestones. Document AI use with "Disclose, Verify, Critique":


## AI Tools Used
-GitHub Copilot 

**Tool**: GitHub Copilot (VS Code extension)  
**Model**: Claude Haiku 4.5


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

## Summary
**Total AI use**: 9 primary tasks (data pipeline generation, documentation,edits,analysis)  
**Primary use cases**: Data ETL scripting, pandas aggregation logic, documentation templates, review, edits, formatting
**Verification method**: All code tested against real data with dimension validation and output checks, as well as checked by all members of the team

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

**Date**: February 24, 2026  
**Tool**: GitHub Copilot (Claude Haiku 4.5)  
**Status**: ✅ Compliant
