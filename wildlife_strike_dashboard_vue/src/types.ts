export type RiskLevel = "Low" | "Moderate" | "High" | "Critical";

export interface SummaryRow {
  total_reports: number;
  damaged_cases: number;
  damage_rate: number;
  final_model: string;
  final_threshold: number;
}

export interface RiskRow {
  category: string;
  total_count: number;
  damage_count: number;
  damage_rate: number;
  overall_damage_rate: number;
  risk_lift: number;
  min_count_pass: string;
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

export interface FeatureRow {
  feature: string;
  importance: number;
}

export interface OperatorRow {
  OPERATOR: string;
  total: number;
  damaged: number;
  damage_rate: number;
}

export interface AirportRow {
  AIRPORT: string;
  LATITUDE: number;
  LONGITUDE: number;
  total: number;
  damaged: number;
  damage_rate: number;
}

export interface AirportProfileRow {
  AIRPORT: string;
  dominant_phase: string;
  common_altitude_group: string;
  common_size: string;
  common_species: string;
}

export interface ConfusionRow {
  rowLabel: string;
  pred_0: number;
  pred_1: number;
}

export interface MonthlyTrendRow {
  INCIDENT_MONTH: number;
  total_count: number;
  damage_count: number;
  damage_rate: number;
}

export interface AssessmentScenarioRow {
  scenario_id: string;
  PHASE_OF_FLIGHT: string;
  ALTITUDE_GROUP: string;
  DISTANCE_GROUP: string;
  SPECIES: string;
  SIZE_CLEAN: string;
  AC_MASS: string;
  TYPE_ENG: string;
  NUM_ENGS: number;
  SKY_CLEAN: string;
  Damage_Binary: number;
  phase_rate: number;
  size_rate: number;
  altitude_rate: number;
  distance_rate: number;
  risk_score: number;
  recommendation: string;
}

export interface IncidentRow {
  report_id: string;
  OPID: string;
  OPERATOR: string;
  AIRPORT: string;
  LATITUDE: number;
  LONGITUDE: number;
  INCIDENT_MONTH: number;
  PHASE_OF_FLIGHT: string;
  ALTITUDE_GROUP: string;
  DISTANCE_GROUP: string;
  SIZE_CLEAN: string;
  SPECIES: string;
  AC_MASS: string;
  SKY_CLEAN: string;
  Damage_Binary: number;
  phase_rate: number;
  size_rate: number;
  altitude_rate: number;
  scenario_risk: number;
}

export interface StrikeRecord {
  INCIDENT_MONTH: number;
  TIME_OF_DAY: string;
  PHASE_OF_FLIGHT: string;
  ALTITUDE_GROUP: string;
  DISTANCE_GROUP: string;
  SPECIES: string;
  SIZE_CLEAN: string;
  NUM_STRUCK: string;
  AC_CLASS: string;
  AC_MASS: string;
  TYPE_ENG: string;
  NUM_ENGS: number;
  FAAREGION: string;
  STATE: string;
  SKY_CLEAN: string;
  Damage_Binary: number;
}
