import { describe, expect, it } from 'vitest';
import { assignRiskLevel, calculateDamageRate, classifyQuadrant } from '../src/utils/risk';
import type { StrikeRecord } from '../src/types';

describe('risk utilities', () => {
  const rows: StrikeRecord[] = [
    { Damage_Binary: 1, PHASE_OF_FLIGHT: 'Climb' },
    { Damage_Binary: 0, PHASE_OF_FLIGHT: 'Climb' },
    { Damage_Binary: 0, PHASE_OF_FLIGHT: 'Approach' },
    { Damage_Binary: 0, PHASE_OF_FLIGHT: 'Approach' },
    { Damage_Binary: 1, PHASE_OF_FLIGHT: 'Unknown' }
  ];

  it('assigns risk levels from damage-rate percentages', () => {
    expect(assignRiskLevel(4.9)).toBe('Low');
    expect(assignRiskLevel(5)).toBe('Moderate');
    expect(assignRiskLevel(10)).toBe('High');
    expect(assignRiskLevel(20)).toBe('Critical');
  });

  it('calculates grouped damage rate and minimum sample flags', () => {
    const stats = calculateDamageRate(rows, 'PHASE_OF_FLIGHT', 2);
    const climb = stats.find((row) => row.category === 'Climb');
    const unknown = stats.find((row) => row.category === 'Unknown');

    expect(climb?.collisionCount).toBe(2);
    expect(climb?.damagedCount).toBe(1);
    expect(climb?.damageRate).toBe(50);
    expect(climb?.riskLevel).toBe('Critical');
    expect(climb?.minCountPass).toBe(true);
    expect(unknown?.minCountPass).toBe(false);
  });

  it('classifies frequency-severity quadrants', () => {
    expect(classifyQuadrant(100, 12, 50, 7)).toBe('Priority Risk');
    expect(classifyQuadrant(10, 12, 50, 7)).toBe('Hidden Risk');
    expect(classifyQuadrant(100, 3, 50, 7)).toBe('Frequent but Lower Damage');
    expect(classifyQuadrant(10, 3, 50, 7)).toBe('Low Priority');
  });
});
