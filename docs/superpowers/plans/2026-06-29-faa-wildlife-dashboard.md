# FAA Wildlife Dashboard Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a maintainable Streamlit dashboard that presents FAA wildlife strike aircraft damage risk results from the existing pipeline outputs.

**Architecture:** Create a new `wildlife_strike_dashboard/` app beside `FAA_Wildlife_Damage_Final/`. Data loading, schema normalization, filtering, risk aggregation, charts, and visual explanation panels are separated into focused modules so pages stay small and maintainable. The dashboard reads existing CSV/PNG/PKL artifacts in place instead of duplicating pipeline outputs.

**Tech Stack:** Python, Streamlit, pandas, Plotly, joblib, pytest.

---

## Source Understanding

The GPT-written design document, `대시보드 구현설계서_v0.docx`, describes a six-page demonstration dashboard:

- `Risk Overview`: total cases, damaged cases, damage rate, target imbalance, monthly trends.
- `Flight Condition Explorer`: phase, altitude, distance, and phase-altitude heatmap.
- `Wildlife Impact Explorer`: wildlife size, number struck, species top risks.
- `Frequency-Severity Matrix`: distinguish frequent conditions from high-damage-rate conditions.
- `Model Performance`: emphasize recall and F1 over accuracy, with confusion matrix, PR/ROC, and feature importance.
- `Final Insight`: final presentation cards focused on "frequency does not equal risk".

The actual output folder already contains the needed artifacts:

- Data: `FAA_Wildlife_Damage_Final/01_data/processed_modeling_data.csv`
- Metrics: `FAA_Wildlife_Damage_Final/04_metrics/metrics_table.csv`, `final_model_metrics.csv`, `final_confusion_matrix.csv`
- Predictions: `FAA_Wildlife_Damage_Final/03_predictions/*.csv`
- Risk tables: `FAA_Wildlife_Damage_Final/06_tables/risk_by_*.csv`
- Feature importance: `FAA_Wildlife_Damage_Final/06_tables/feature_importance.csv`, `feature_importance_encoded.csv`
- Existing figures: `FAA_Wildlife_Damage_Final/05_figures/*.png`

Important schema differences from the design:

- `processed_modeling_data.csv` does not include `INCIDENT_YEAR`, so the first dashboard version should not expose a year filter.
- Metrics use column `f1`, not `f1_score`.
- Predictions use `y_true`, `y_pred`, `y_proba`, `model_name`, `split`.
- Altitude groups include values such as `501-1,500 ft`, not only the simplified labels in the design.

---

## Plan Iteration Log

### 1st Plan

Build the design document literally: create all six pages, copy data into `wildlife_strike_dashboard/data`, create many static SVG files under `assets`, implement every filter listed in the design, and load each page independently.

### Expert Review of 1st Plan

Issues found:

- The design assumes fields that do not exist, especially `INCIDENT_YEAR`.
- Copying pipeline outputs into dashboard-local `data/` creates stale-data risk.
- Static SVG files for every explainer add maintenance burden for a student/demo project.
- Page-level independent loading would duplicate logic and make filter bugs likely.
- The model page needs schema normalization because `f1_score` in the design is actually `f1` in the CSV.

Decision: rewrite the plan around a data contract layer, shared filter state, generated SVG/HTML explainers, and in-place artifact reads.

### 2nd Plan

Create a maintainable Streamlit app that reads existing outputs directly. Implement shared modules first: paths, data loader, schema normalization, filters, risk calculation, chart builders, and visual explainer components. Then implement pages in priority order.

### Expert Review of 2nd Plan

Remaining issues found:

- Global Streamlit filters must be rendered from one shared function to avoid inconsistent page behavior.
- Tests should target the risk and normalization utilities before UI pages.
- Model performance should gracefully handle unavailable model-specific confusion matrices by computing them from prediction CSVs.
- The visual explainer should be code-generated SVG/HTML for selected states, not a collection of near-duplicate files.

Decision: final plan below passes review after adding explicit tests, one shared sidebar contract, and prediction-derived confusion matrices.

---

## Final Reviewed Implementation Plan

### Task 1: App Scaffold and Configuration

**Files:**
- Create: `wildlife_strike_dashboard/app.py`
- Create: `wildlife_strike_dashboard/requirements.txt`
- Create: `wildlife_strike_dashboard/README.md`
- Create: `wildlife_strike_dashboard/config.py`
- Create: `wildlife_strike_dashboard/pages/01_overview.py`
- Create: `wildlife_strike_dashboard/pages/02_flight_condition.py`
- Create: `wildlife_strike_dashboard/pages/03_wildlife_impact.py`
- Create: `wildlife_strike_dashboard/pages/04_frequency_severity.py`
- Create: `wildlife_strike_dashboard/pages/05_model_performance.py`
- Create: `wildlife_strike_dashboard/pages/06_final_insight.py`

- [ ] **Step 1: Create dashboard folders**: `components/`, `utils/`, `pages/`, `tests/`.
- [ ] **Step 2: Add requirements**: `streamlit`, `pandas`, `plotly`, `joblib`, `scikit-learn`, `pytest`.
- [ ] **Step 3: Add `config.py`** with one source of truth for paths pointing to `../FAA_Wildlife_Damage_Final`.
- [ ] **Step 4: Add `app.py`** with Streamlit page config, dashboard title, and overview landing content.
- [ ] **Step 5: Run** `streamlit run wildlife_strike_dashboard/app.py` and confirm the app starts.

### Task 2: Data Contract and Tests

**Files:**
- Create: `wildlife_strike_dashboard/utils/data_loader.py`
- Create: `wildlife_strike_dashboard/utils/schema.py`
- Create: `wildlife_strike_dashboard/tests/test_schema.py`
- Create: `wildlife_strike_dashboard/tests/test_data_loader.py`

- [ ] **Step 1: Write tests** for loading `processed_modeling_data.csv`, normalizing metrics `f1` to a display label, and handling missing `INCIDENT_YEAR`.
- [ ] **Step 2: Implement cached CSV loaders** using `st.cache_data` where Streamlit is available and plain pandas functions for tests.
- [ ] **Step 3: Implement schema helpers**:
  - `available_filter_columns(df)`
  - `normalize_metrics_columns(metrics_df)`
  - `load_prediction_files(paths)`
  - `validate_required_columns(df, required_columns)`
- [ ] **Step 4: Run** `pytest wildlife_strike_dashboard/tests/test_schema.py wildlife_strike_dashboard/tests/test_data_loader.py -q`.

### Task 3: Shared Risk, Filters, and Styling

**Files:**
- Create: `wildlife_strike_dashboard/utils/risk.py`
- Create: `wildlife_strike_dashboard/components/filter_panel.py`
- Create: `wildlife_strike_dashboard/components/kpi_cards.py`
- Create: `wildlife_strike_dashboard/components/style.py`
- Create: `wildlife_strike_dashboard/tests/test_risk.py`

- [ ] **Step 1: Write tests** for `calculate_damage_rate`, `assign_risk_level`, minimum-count filtering, and filter application.
- [ ] **Step 2: Implement `calculate_damage_rate(df, group_col)`** returning `category`, `collision_count`, `damaged_count`, `damage_rate`, and `risk_level`.
- [ ] **Step 3: Implement shared sidebar filters** only for columns present in the actual data.
- [ ] **Step 4: Add minimum sample selector** with values `30`, `50`, `100`, `200`, default `50`.
- [ ] **Step 5: Add dark dashboard CSS** matching the design colors, while keeping cards at a maintainable 8px radius unless Streamlit defaults force otherwise.
- [ ] **Step 6: Run** `pytest wildlife_strike_dashboard/tests/test_risk.py -q`.

### Task 4: Chart Builders

**Files:**
- Create: `wildlife_strike_dashboard/components/charts.py`
- Create: `wildlife_strike_dashboard/tests/test_charts_data.py`

- [ ] **Step 1: Write tests** for chart input data preparation, not Plotly rendering internals.
- [ ] **Step 2: Implement reusable chart functions**:
  - `damage_donut(df)`
  - `monthly_count_damage_rate(df)`
  - `damage_rate_bar(stats_df, title)`
  - `phase_altitude_heatmap(df, min_count)`
  - `frequency_severity_matrix(df, group_col, min_count)`
  - `model_metric_comparison(metrics_df)`
  - `confusion_matrix_from_predictions(pred_df)`
  - `feature_importance_top_n(feature_df, n=10)`
- [ ] **Step 3: Use one Plotly template** with the dashboard dark theme.
- [ ] **Step 4: Run** `pytest wildlife_strike_dashboard/tests/test_charts_data.py -q`.

### Task 5: Visual Explainer Components

**Files:**
- Create: `wildlife_strike_dashboard/components/visual_explainer.py`

- [ ] **Step 1: Implement generated SVG/HTML explainers**:
  - `render_collision_concept()`
  - `render_flight_phase_explainer(selected_phase, phase_stats)`
  - `render_altitude_explainer(selected_altitude, altitude_stats)`
  - `render_wildlife_size_explainer(selected_size, size_stats)`
  - `render_num_struck_explainer(selected_num_struck, num_stats)`
- [ ] **Step 2: Include damage rate and average difference badges in every selected-state explainer.**
- [ ] **Step 3: Keep all explainer copy within the approved wording: "시연형 분석 대시보드", "손상 위험 탐색", "손상 가능성 추정", and avoid real-time/operational claims.**

### Task 6: Implement Pages in Presentation Priority Order

**Files:**
- Modify: `wildlife_strike_dashboard/pages/01_overview.py`
- Modify: `wildlife_strike_dashboard/pages/02_flight_condition.py`
- Modify: `wildlife_strike_dashboard/pages/03_wildlife_impact.py`
- Modify: `wildlife_strike_dashboard/pages/04_frequency_severity.py`
- Modify: `wildlife_strike_dashboard/pages/05_model_performance.py`
- Modify: `wildlife_strike_dashboard/pages/06_final_insight.py`

- [ ] **Step 1: Overview**: KPI cards, damage donut, monthly count/damage-rate combo chart, collision concept explainer.
- [ ] **Step 2: Flight Condition**: phase bar, altitude bar, phase-altitude heatmap, phase and altitude explainers.
- [ ] **Step 3: Wildlife Impact**: size bar, number-struck bar, species top 10, wildlife explainers.
- [ ] **Step 4: Frequency-Severity Matrix**: selectable group column from actual available fields and quadrant summary.
- [ ] **Step 5: Model Performance**: recall/F1 emphasized cards, model comparison, prediction-derived confusion matrix, PR/ROC from prediction probabilities, feature importance top 10.
- [ ] **Step 6: Final Insight**: three presentation cards and one concise summary sentence.

### Task 7: Verification

**Files:**
- Run: `pytest wildlife_strike_dashboard/tests -q`
- Run: `streamlit run wildlife_strike_dashboard/app.py`

- [ ] **Step 1: Run all dashboard utility tests.**
- [ ] **Step 2: Start the Streamlit app.**
- [ ] **Step 3: Open each page and confirm no missing-column errors.**
- [ ] **Step 4: Change sidebar filters and confirm KPI/charts update.**
- [ ] **Step 5: Verify the Model Performance page emphasizes Recall and F1 over Accuracy.**
- [ ] **Step 6: Verify no page uses prohibited wording such as "실시간 위험 예측" or "항공기 손상 확정".**

---

## Final Expert Review Result

No blocking issues remain for implementation.

Implementation should proceed with Task 1 through Task 7 in order. The most important guardrail is to implement the schema/data contract before pages, because the design document and actual artifacts differ in small but important ways. The second guardrail is to keep explainers generated from code rather than maintaining many separate SVG files for the first version.
