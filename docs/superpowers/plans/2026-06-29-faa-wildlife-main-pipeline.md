# FAA Wildlife Main Pipeline Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build the Main Pipeline deliverables for FAA Wildlife Strike aircraft damage prediction, excluding the Streamlit dashboard for this first pass.

**Architecture:** A small Python package under `FAA_Wildlife_Damage_Final/src` owns reusable pipeline logic, while `run_main_pipeline.py` executes the full workflow from the source Excel workbook to CSV, PKL, PNG, and Markdown outputs. Tests cover leakage prevention, rare-category grouping, data splitting, and threshold selection before the production pipeline is implemented.

**Tech Stack:** Python, pandas, scikit-learn, matplotlib, joblib, openpyxl, pytest, uv.

---

### Task 1: Core Pipeline Contracts

**Files:**
- Create: `FAA_Wildlife_Damage_Final/tests/test_pipeline_core.py`
- Create: `FAA_Wildlife_Damage_Final/src/pipeline_core.py`

- [ ] **Step 1: Write failing tests** for leakage column detection, rare-category grouping, stratified split sizes, and validation threshold selection.
- [ ] **Step 2: Run tests to verify they fail** because `pipeline_core.py` is not implemented.
- [ ] **Step 3: Implement minimal reusable pipeline functions** in `pipeline_core.py`.
- [ ] **Step 4: Run tests to verify they pass.**

### Task 2: Main Pipeline Runner

**Files:**
- Create: `FAA_Wildlife_Damage_Final/run_main_pipeline.py`
- Create: `FAA_Wildlife_Damage_Final/00_config/config.yaml`
- Create output folders from the document-defined Main Pipeline structure.

- [ ] **Step 1: Implement source workbook loading and validation.**
- [ ] **Step 2: Implement official train/test and internal validation splits.**
- [ ] **Step 3: Implement train-only preprocessing with missing-value handling, rare-category grouping, and one-hot encoding.**
- [ ] **Step 4: Train Logistic Regression, Decision Tree, and RandomForest.**
- [ ] **Step 5: Save models, predictions, metrics, threshold experiments, risk tables, feature importance, figures, and Markdown reports.**

### Task 3: Verification

**Files:**
- Run: `pytest FAA_Wildlife_Damage_Final/tests -q`
- Run: `python FAA_Wildlife_Damage_Final/run_main_pipeline.py`

- [ ] **Step 1: Run the test suite.**
- [ ] **Step 2: Run the full Main Pipeline.**
- [ ] **Step 3: Verify required files exist in `01_data` through `07_reports`.**
- [ ] **Step 4: Inspect summary metrics and confirm final threshold came from validation, not test.**
