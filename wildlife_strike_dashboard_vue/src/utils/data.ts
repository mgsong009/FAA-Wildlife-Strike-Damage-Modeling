import Papa from 'papaparse';
import type { MetricRow, PredictionRow, StrikeRecord } from '../types';

export interface NormalizedMetricRow extends MetricRow {
  displayMetrics: Record<string, number>;
}

const DATA_BASE = '/data';

export function parseCsv<T extends object = Record<string, unknown>>(csv: string): T[] {
  const parsed = Papa.parse<T>(csv, {
    header: true,
    dynamicTyping: true,
    skipEmptyLines: true
  });

  if (parsed.errors.length > 0) {
    throw new Error(parsed.errors.map((error) => error.message).join(', '));
  }

  return parsed.data;
}

async function fetchCsv<T extends object>(path: string): Promise<T[]> {
  const response = await fetch(path);
  if (!response.ok) {
    throw new Error(`Could not load ${path}: ${response.status}`);
  }
  return parseCsv<T>(await response.text());
}

export function normalizeMetricRows(rows: MetricRow[]): NormalizedMetricRow[] {
  return rows.map((row) => ({
    ...row,
    displayMetrics: {
      Recall: Number(row.recall),
      'F1-score': Number(row.f1),
      Precision: Number(row.precision),
      'ROC-AUC': Number(row.roc_auc),
      Accuracy: Number(row.accuracy)
    }
  }));
}

export async function loadDashboardData() {
  const [
    strikes,
    metrics,
    finalMetrics,
    logisticPredictions,
    treePredictions,
    rfPredictions,
    finalPredictions,
    featureImportance
  ] = await Promise.all([
    fetchCsv<StrikeRecord>(`${DATA_BASE}/processed_modeling_data.csv`),
    fetchCsv<MetricRow>(`${DATA_BASE}/metrics_table.csv`),
    fetchCsv<MetricRow>(`${DATA_BASE}/final_model_metrics.csv`),
    fetchCsv<PredictionRow>(`${DATA_BASE}/logistic_predictions.csv`),
    fetchCsv<PredictionRow>(`${DATA_BASE}/tree_predictions.csv`),
    fetchCsv<PredictionRow>(`${DATA_BASE}/rf_predictions.csv`),
    fetchCsv<PredictionRow>(`${DATA_BASE}/final_model_predictions.csv`),
    fetchCsv<Record<string, string | number>>(`${DATA_BASE}/feature_importance.csv`)
  ]);

  return {
    strikes,
    metrics: normalizeMetricRows(metrics),
    finalMetrics: normalizeMetricRows(finalMetrics),
    predictions: [...logisticPredictions, ...treePredictions, ...rfPredictions, ...finalPredictions],
    featureImportance
  };
}

export function formatPercent(value: number, digits = 1): string {
  return `${value.toFixed(digits)}%`;
}

export function compactNumber(value: number): string {
  return new Intl.NumberFormat('en-US').format(value);
}
