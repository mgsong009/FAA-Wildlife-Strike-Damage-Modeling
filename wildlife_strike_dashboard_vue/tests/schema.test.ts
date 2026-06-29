import { describe, expect, it } from 'vitest';
import { normalizeMetricRows, parseCsv } from '../src/utils/data';

describe('data schema utilities', () => {
  it('parses numeric CSV fields and keeps text fields', () => {
    const rows = parseCsv('model_name,recall,f1\nDecision Tree,0.38,0.41');
    expect(rows).toEqual([{ model_name: 'Decision Tree', recall: 0.38, f1: 0.41 }]);
  });

  it('normalizes f1 to a stable display metric without requiring f1_score', () => {
    const [row] = normalizeMetricRows([
      {
        model_name: 'Decision Tree',
        split: 'test',
        threshold: 0.85,
        accuracy: 0.92,
        precision: 0.46,
        recall: 0.38,
        f1: 0.41,
        roc_auc: 0.83,
        pr_auc: 0.39
      }
    ]);

    expect(row.f1).toBe(0.41);
    expect(row.displayMetrics).toEqual({
      Recall: 0.38,
      'F1-score': 0.41,
      Precision: 0.46,
      'ROC-AUC': 0.83,
      Accuracy: 0.92
    });
  });
});
