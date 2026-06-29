import type { FilterState, StrikeRecord } from '../types';

const FILTER_COLUMN_MAP: Record<keyof FilterState, keyof StrikeRecord> = {
  month: 'INCIDENT_MONTH',
  phase: 'PHASE_OF_FLIGHT',
  altitude: 'ALTITUDE_GROUP',
  distance: 'DISTANCE_GROUP',
  size: 'SIZE_CLEAN',
  species: 'SPECIES',
  numStruck: 'NUM_STRUCK',
  acClass: 'AC_CLASS',
  acMass: 'AC_MASS',
  faaRegion: 'FAAREGION',
  state: 'STATE'
};

export function createEmptyFilters(): FilterState {
  return {
    month: [],
    phase: [],
    altitude: [],
    distance: [],
    size: [],
    species: [],
    numStruck: [],
    acClass: [],
    acMass: [],
    faaRegion: [],
    state: []
  };
}

export function filterOptions(rows: StrikeRecord[], column: keyof StrikeRecord): string[] {
  return Array.from(
    new Set(
      rows
        .map((row) => row[column])
        .filter((value) => value !== undefined && value !== '')
        .map((value) => String(value))
    )
  ).sort((a, b) => a.localeCompare(b, 'ko', { numeric: true }));
}

export function applyFilters(rows: StrikeRecord[], filters: FilterState): StrikeRecord[] {
  return rows.filter((row) =>
    Object.entries(FILTER_COLUMN_MAP).every(([filterKey, column]) => {
      const selected = filters[filterKey as keyof FilterState];
      if (selected.length === 0) return true;
      return selected.includes(String(row[column]));
    })
  );
}

export function filterLabel(key: keyof FilterState): string {
  const labels: Record<keyof FilterState, string> = {
    month: 'Month',
    phase: 'Flight Phase',
    altitude: 'Altitude Group',
    distance: 'Airport Distance',
    size: 'Wildlife Size',
    species: 'Species',
    numStruck: 'Number Struck',
    acClass: 'Aircraft Class',
    acMass: 'Aircraft Mass',
    faaRegion: 'FAA Region',
    state: 'State'
  };
  return labels[key];
}

export function filterColumn(key: keyof FilterState): keyof StrikeRecord {
  return FILTER_COLUMN_MAP[key];
}
