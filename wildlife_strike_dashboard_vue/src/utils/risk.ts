import type { RiskLevel, RiskStat, StrikeRecord } from '../types';

export type QuadrantLabel =
  | 'Priority Risk'
  | 'Hidden Risk'
  | 'Frequent but Lower Damage'
  | 'Low Priority';

export function assignRiskLevel(ratePercent: number): RiskLevel {
  if (ratePercent < 5) return 'Low';
  if (ratePercent < 10) return 'Moderate';
  if (ratePercent < 20) return 'High';
  return 'Critical';
}

export function calculateOverallDamageRate(rows: StrikeRecord[]): number {
  if (rows.length === 0) return 0;
  const damaged = rows.reduce((sum, row) => sum + Number(row.Damage_Binary || 0), 0);
  return (damaged / rows.length) * 100;
}

export function calculateDamageRate(
  rows: StrikeRecord[],
  groupCol: keyof StrikeRecord,
  minCount = 50
): RiskStat[] {
  const grouped = new Map<string, { collisionCount: number; damagedCount: number }>();
  const overallDamageRate = calculateOverallDamageRate(rows);

  for (const row of rows) {
    const rawValue = row[groupCol];
    const category = rawValue === undefined || rawValue === '' ? 'Unknown' : String(rawValue);
    const current = grouped.get(category) ?? { collisionCount: 0, damagedCount: 0 };
    current.collisionCount += 1;
    current.damagedCount += Number(row.Damage_Binary || 0);
    grouped.set(category, current);
  }

  return Array.from(grouped.entries())
    .map(([category, value]) => {
      const damageRate = value.collisionCount === 0 ? 0 : (value.damagedCount / value.collisionCount) * 100;
      const riskLift = overallDamageRate === 0 ? 0 : damageRate / overallDamageRate;

      return {
        category,
        collisionCount: value.collisionCount,
        damagedCount: value.damagedCount,
        damageRate,
        overallDamageRate,
        riskLift,
        riskLevel: assignRiskLevel(damageRate),
        minCountPass: value.collisionCount >= minCount
      };
    })
    .sort((a, b) => b.damageRate - a.damageRate);
}

export function classifyQuadrant(
  collisionCount: number,
  damageRate: number,
  collisionBaseline: number,
  damageRateBaseline: number
): QuadrantLabel {
  const highFrequency = collisionCount >= collisionBaseline;
  const highSeverity = damageRate >= damageRateBaseline;

  if (highFrequency && highSeverity) return 'Priority Risk';
  if (!highFrequency && highSeverity) return 'Hidden Risk';
  if (highFrequency && !highSeverity) return 'Frequent but Lower Damage';
  return 'Low Priority';
}

export function median(values: number[]): number {
  if (values.length === 0) return 0;
  const sorted = [...values].sort((a, b) => a - b);
  const middle = Math.floor(sorted.length / 2);
  return sorted.length % 2 === 0 ? (sorted[middle - 1] + sorted[middle]) / 2 : sorted[middle];
}
