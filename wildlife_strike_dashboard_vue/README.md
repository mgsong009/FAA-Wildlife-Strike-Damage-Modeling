# FAA Wildlife Strike Damage Risk Dashboard

Vue 3 + TypeScript SPA for exploring the FAA wildlife strike aircraft damage analysis outputs.

## Run

```powershell
npm.cmd install
npm.cmd run dev
```

Open the local Vite URL shown in the terminal.

## Data

The app reads static CSV files from `public/data`. These files were copied from:

- `../FAA_Wildlife_Damage_Final/01_data/processed_modeling_data.csv`
- `../FAA_Wildlife_Damage_Final/04_metrics/*.csv`
- `../FAA_Wildlife_Damage_Final/03_predictions/*.csv`
- `../FAA_Wildlife_Damage_Final/06_tables/feature_importance.csv`

If the modeling pipeline is rerun, copy the latest CSV files into `public/data` before building the SPA.
