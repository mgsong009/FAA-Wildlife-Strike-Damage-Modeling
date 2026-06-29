import type { MetricRow, PredictionRow, RiskStat, StrikeRecord } from '../types';
import { calculateDamageRate, classifyQuadrant, median } from './risk';

type Data = Record<string, unknown>;
type Layout = Record<string, unknown>;

export interface PlotSpec {
  data: Data[];
  layout: Partial<Layout>;
}

const transparentLayout: Partial<Layout> = {
  paper_bgcolor: 'rgba(0,0,0,0)',
  plot_bgcolor: 'rgba(0,0,0,0)',
  font: { color: '#f8fafc', family: 'Inter, system-ui, sans-serif' },
  margin: { l: 48, r: 24, t: 36, b: 48 },
  legend: { orientation: 'h' }
};

const riskColors: Record<string, string> = {
  Low: '#38BDF8',
  Moderate: '#FACC15',
  High: '#FB923C',
  Critical: '#EF4444'
};

export function damageDonut(rows: StrikeRecord[]): PlotSpec {
  const damaged = rows.reduce((sum, row) => sum + Number(row.Damage_Binary || 0), 0);
  const undamaged = rows.length - damaged;
  return {
    data: [
      {
        type: 'pie',
        hole: 0.62,
        values: [undamaged, damaged],
        labels: ['No Damage', 'Damage'],
        marker: { colors: ['#22D3EE', '#EF4444'] },
        textinfo: 'label+percent'
      }
    ],
    layout: { ...transparentLayout, title: { text: 'Damage vs No Damage' } }
  };
}

export function monthlyTrend(rows: StrikeRecord[]): PlotSpec {
  const stats = calculateDamageRate(rows, 'INCIDENT_MONTH', 1).sort((a, b) =>
    a.category.localeCompare(b.category, 'ko', { numeric: true })
  );
  return {
    data: [
      {
        type: 'bar',
        name: 'Collision count',
        x: stats.map((row) => row.category),
        y: stats.map((row) => row.collisionCount),
        marker: { color: '#22D3EE' },
        yaxis: 'y'
      },
      {
        type: 'scatter',
        mode: 'lines+markers',
        name: 'Damage rate',
        x: stats.map((row) => row.category),
        y: stats.map((row) => row.damageRate),
        marker: { color: '#FB923C' },
        yaxis: 'y2'
      }
    ],
    layout: {
      ...transparentLayout,
      title: { text: 'Monthly Count vs Damage Rate' },
      yaxis: { title: { text: 'Count' } },
      yaxis2: { title: { text: 'Damage %' }, overlaying: 'y', side: 'right' }
    }
  };
}

export function riskBar(stats: RiskStat[], title: string, limit = 12): PlotSpec {
  const rows = stats.filter((row) => row.minCountPass).slice(0, limit);
  return {
    data: [
      {
        type: 'bar',
        x: rows.map((row) => row.category),
        y: rows.map((row) => row.damageRate),
        text: rows.map((row) => `${row.damageRate.toFixed(1)}%`),
        marker: { color: rows.map((row) => riskColors[row.riskLevel]) }
      }
    ],
    layout: { ...transparentLayout, title: { text: title }, yaxis: { title: { text: 'Damage rate (%)' } } }
  };
}

export function phaseAltitudeHeatmap(rows: StrikeRecord[], minCount: number): PlotSpec {
  const phases = Array.from(new Set(rows.map((row) => String(row.PHASE_OF_FLIGHT ?? 'Unknown')))).sort();
  const altitudes = Array.from(new Set(rows.map((row) => String(row.ALTITUDE_GROUP ?? 'Unknown')))).sort((a, b) =>
    a.localeCompare(b, 'ko', { numeric: true })
  );
  const z = phases.map((phase) =>
    altitudes.map((altitude) => {
      const subset = rows.filter(
        (row) => String(row.PHASE_OF_FLIGHT ?? 'Unknown') === phase && String(row.ALTITUDE_GROUP ?? 'Unknown') === altitude
      );
      if (subset.length < minCount) return null;
      const damaged = subset.reduce((sum, row) => sum + Number(row.Damage_Binary || 0), 0);
      return (damaged / subset.length) * 100;
    })
  );

  return {
    data: [
      {
        type: 'heatmap',
        x: altitudes,
        y: phases,
        z,
        colorscale: [
          [0, '#0EA5E9'],
          [0.4, '#FACC15'],
          [0.7, '#FB923C'],
          [1, '#EF4444']
        ],
        hovertemplate: 'Phase=%{y}<br>Altitude=%{x}<br>Damage=%{z:.1f}%<extra></extra>'
      }
    ],
    layout: { ...transparentLayout, title: { text: 'Phase x Altitude Risk Heatmap' } }
  };
}

export function frequencySeverityMatrix(stats: RiskStat[]): PlotSpec {
  const rows = stats.filter((row) => row.minCountPass);
  const collisionBaseline = median(rows.map((row) => row.collisionCount));
  const damageBaseline = rows[0]?.overallDamageRate ?? 0;

  return {
    data: [
      {
        type: 'scatter',
        mode: 'markers+text',
        x: rows.map((row) => row.collisionCount),
        y: rows.map((row) => row.damageRate),
        text: rows.map((row) => row.category),
        textposition: 'top center',
        marker: {
          size: rows.map((row) => Math.max(10, Math.sqrt(row.damagedCount) * 3)),
          color: rows.map((row) => riskColors[row.riskLevel]),
          opacity: 0.82
        },
        customdata: rows.map((row) =>
          classifyQuadrant(row.collisionCount, row.damageRate, collisionBaseline, damageBaseline)
        ),
        hovertemplate: '%{text}<br>Count=%{x}<br>Damage=%{y:.1f}%<br>%{customdata}<extra></extra>'
      }
    ],
    layout: {
      ...transparentLayout,
      title: { text: 'Frequency-Severity Matrix' },
      xaxis: { title: { text: 'Collision count' } },
      yaxis: { title: { text: 'Damage rate (%)' } },
      shapes: [
        { type: 'line', x0: collisionBaseline, x1: collisionBaseline, y0: 0, y1: 1, yref: 'paper', line: { color: '#94A3B8', dash: 'dot' } },
        { type: 'line', x0: 0, x1: 1, xref: 'paper', y0: damageBaseline, y1: damageBaseline, line: { color: '#94A3B8', dash: 'dot' } }
      ]
    }
  };
}

export function modelMetricComparison(metrics: MetricRow[]): PlotSpec {
  const testRows = metrics.filter((row) => String(row.split).includes('test'));
  return {
    data: [
      {
        type: 'bar',
        name: 'Recall',
        x: testRows.map((row) => row.model_name),
        y: testRows.map((row) => Number(row.recall)),
        marker: { color: '#2DD4BF' }
      },
      {
        type: 'bar',
        name: 'F1-score',
        x: testRows.map((row) => row.model_name),
        y: testRows.map((row) => Number(row.f1)),
        marker: { color: '#22D3EE' }
      }
    ],
    layout: { ...transparentLayout, title: { text: 'Recall and F1-score by Model' }, barmode: 'group' }
  };
}

export function confusionMatrix(predictions: PredictionRow[], selectedModel: string): PlotSpec {
  const rows = predictions.filter((row) => row.model_name === selectedModel);
  const tn = rows.filter((row) => row.y_true === 0 && row.y_pred === 0).length;
  const fp = rows.filter((row) => row.y_true === 0 && row.y_pred === 1).length;
  const fn = rows.filter((row) => row.y_true === 1 && row.y_pred === 0).length;
  const tp = rows.filter((row) => row.y_true === 1 && row.y_pred === 1).length;

  return {
    data: [
      {
        type: 'heatmap',
        x: ['Pred 0', 'Pred 1'],
        y: ['True 0', 'True 1'],
        z: [
          [tn, fp],
          [fn, tp]
        ],
        text: [
          [String(tn), String(fp)],
          [String(fn), String(tp)]
        ],
        texttemplate: '%{text}',
        colorscale: [
          [0, '#132238'],
          [1, '#22D3EE']
        ]
      }
    ],
    layout: { ...transparentLayout, title: { text: `${selectedModel} Confusion Matrix` } }
  };
}

export function featureImportance(rows: Record<string, string | number>[]): PlotSpec {
  const sorted = [...rows]
    .sort((a, b) => Number(b.importance ?? 0) - Number(a.importance ?? 0))
    .slice(0, 10)
    .reverse();
  return {
    data: [
      {
        type: 'bar',
        orientation: 'h',
        x: sorted.map((row) => Number(row.importance ?? 0)),
        y: sorted.map((row) => String(row.feature)),
        marker: { color: '#2DD4BF' }
      }
    ],
    layout: { ...transparentLayout, title: { text: 'Feature Importance Top 10' } }
  };
}
