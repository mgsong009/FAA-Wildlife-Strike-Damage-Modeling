import { describe, expect, it } from 'vitest';
import { applyFilters, createEmptyFilters, filterOptions } from '../src/utils/filters';
import type { StrikeRecord } from '../src/types';

describe('filter utilities', () => {
  const rows: StrikeRecord[] = [
    { Damage_Binary: 1, INCIDENT_MONTH: 1, PHASE_OF_FLIGHT: 'Climb', SIZE_CLEAN: 'Large' },
    { Damage_Binary: 0, INCIDENT_MONTH: 2, PHASE_OF_FLIGHT: 'Approach', SIZE_CLEAN: 'Small' },
    { Damage_Binary: 0, INCIDENT_MONTH: 2, PHASE_OF_FLIGHT: 'Climb', SIZE_CLEAN: 'Small' }
  ];

  it('builds sorted options only from available values', () => {
    expect(filterOptions(rows, 'PHASE_OF_FLIGHT')).toEqual(['Approach', 'Climb']);
  });

  it('applies multiple selected filters', () => {
    const filters = createEmptyFilters();
    filters.month = ['2'];
    filters.phase = ['Climb'];

    expect(applyFilters(rows, filters)).toEqual([
      { Damage_Binary: 0, INCIDENT_MONTH: 2, PHASE_OF_FLIGHT: 'Climb', SIZE_CLEAN: 'Small' }
    ]);
  });
});
