export interface StrikeRecord {
  Damage_Binary: number;
  INCIDENT_MONTH?: number | string;
  TIME_OF_DAY?: string;
  PHASE_OF_FLIGHT?: string;
  ALTITUDE_GROUP?: string;
  DISTANCE_GROUP?: string;
  SPECIES?: string;
  SIZE_CLEAN?: string;
  NUM_STRUCK?: string | number;
  AC_CLASS?: string;
  AC_MASS?: string | number;
  TYPE_ENG?: string;
  NUM_ENGS?: string | number;
  FAAREGION?: string;
  STATE?: string;
  SKY_CLEAN?: string;
  [key: string]: string | number | undefined;
}

export interface MetricRow {
  model_name: string;
  split: string;
  threshold: number;
  accuracy: number;
  precision: number;
  recall: number;
  f1: number;
  roc_auc: number;
  pr_auc: number;
}

export interface PredictionRow {
  y_true: number;
  y_pred: number;
  y_proba: number;
  model_name: string;
  split: string;
}

export interface RiskStat {
  category: string;
  collisionCount: number;
  damagedCount: number;
  damageRate: number;
  overallDamageRate: number;
  riskLift: number;
  riskLevel: RiskLevel;
  minCountPass: boolean;
}

export type RiskLevel = 'Low' | 'Moderate' | 'High' | 'Critical';

export interface FilterState {
  month: string[];
  phase: string[];
  altitude: string[];
  distance: string[];
  size: string[];
  species: string[];
  numStruck: string[];
  acClass: string[];
  acMass: string[];
  faaRegion: string[];
  state: string[];
}
