# FAA Wildlife Strike Damage Modeling

This repository contains a capstone project for predicting aircraft damage risk from FAA wildlife strike incident data, plus a Vue dashboard for exploring model outputs.

## Project Structure

- `FAA_Wildlife_Damage_Final/` - Python modeling pipeline, tests, metrics, figures, and submission materials.
- `wildlife_strike_dashboard_vue/` - Vue 3 + TypeScript dashboard that reads static CSV outputs from `public/data`.
- `docs/` - Project planning and design documents.

## Modeling Pipeline

```powershell
$env:UV_CACHE_DIR='.uv-cache'
uv run --with pandas --with numpy --with scikit-learn --with matplotlib --with openpyxl --with pyyaml --with joblib python FAA_Wildlife_Damage_Final/run_main_pipeline.py
```

Run tests:

```powershell
$env:UV_CACHE_DIR='.uv-cache'
uv run --with pytest --with pandas --with numpy --with scikit-learn --with matplotlib --with openpyxl --with pyyaml --with joblib pytest FAA_Wildlife_Damage_Final/tests -q
```

## Dashboard

```powershell
cd wildlife_strike_dashboard_vue
npm.cmd install
npm.cmd run dev
```

Build and test:

```powershell
npm.cmd run build
npm.cmd run test
```

## Notes Before Publishing

The repository intentionally ignores local dependency folders, build output, caches, and generated zip archives. Review the data files before publishing publicly, especially original Excel datasets and derived CSV files.

