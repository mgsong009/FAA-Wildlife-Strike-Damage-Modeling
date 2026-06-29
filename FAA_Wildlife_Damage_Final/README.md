# FAA Wildlife Damage Prediction

This project builds the Main Pipeline deliverables for predicting `Damage_Binary`, the aircraft damage indicator after an FAA wildlife strike incident.

## Scope

- Predict damage among already reported wildlife strike incidents.
- Use the document-approved Main Model features only.
- Exclude leakage-prone post-incident fields such as `DAMAGE_LEVEL`, `STR_*`, and `ING_*`.
- Tune classification threshold on validation data only.
- Reserve the test split for final evaluation.

## Run

```powershell
$env:UV_CACHE_DIR='.uv-cache'
uv run --with pandas --with numpy --with scikit-learn --with matplotlib --with openpyxl --with pyyaml --with joblib python FAA_Wildlife_Damage_Final/run_main_pipeline.py
```

## Test

```powershell
$env:UV_CACHE_DIR='.uv-cache'
uv run --with pytest --with pandas --with numpy --with scikit-learn --with matplotlib --with openpyxl --with pyyaml --with joblib pytest FAA_Wildlife_Damage_Final/tests -q
```
