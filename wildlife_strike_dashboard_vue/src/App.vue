<script setup lang="ts">
import { computed, onMounted, ref } from "vue";
import AnalyticsOverview from "./pages/AnalyticsOverview.vue";
import DamageAssessment from "./pages/DamageAssessment.vue";
import FlightPhaseExplorer from "./pages/FlightPhaseExplorer.vue";
import OperatorApplicationDemo from "./pages/OperatorApplicationDemo.vue";
import RiskFactorIntelligence from "./pages/RiskFactorIntelligence.vue";
import type {
  AssessmentScenarioRow,
  FeatureRow,
  IncidentRow,
  MetricRow,
  MonthlyTrendRow,
  OperatorRow,
  RiskRow,
  StrikeRecord,
  SummaryRow,
} from "./types";
import { loadCsv } from "./utils/csv";

type TabId = "analytics" | "assessment" | "phase" | "factors" | "operator";

const tabs: Array<{ id: TabId; label: string; index: string }> = [
  { id: "analytics", label: "Analytics Overview", index: "0" },
  { id: "assessment", label: "Post-Strike Assessment", index: "1" },
  { id: "phase", label: "Flight Phase Risk", index: "2" },
  { id: "factors", label: "Wildlife & Aircraft Factors", index: "3" },
  { id: "operator", label: "Operator / Airport Demo", index: "4" },
];

const activeTab = ref<TabId>("analytics");
const loading = ref(true);
const error = ref("");

const summary = ref<SummaryRow[]>([]);
const monthly = ref<MonthlyTrendRow[]>([]);
const scenarios = ref<AssessmentScenarioRow[]>([]);
const phaseRisk = ref<RiskRow[]>([]);
const sizeRisk = ref<RiskRow[]>([]);
const altitudeRisk = ref<RiskRow[]>([]);
const numRisk = ref<RiskRow[]>([]);
const speciesRisk = ref<RiskRow[]>([]);
const distanceRisk = ref<RiskRow[]>([]);
const metrics = ref<MetricRow[]>([]);
const finalMetrics = ref<MetricRow[]>([]);
const features = ref<FeatureRow[]>([]);
const operators = ref<OperatorRow[]>([]);
const incidents = ref<IncidentRow[]>([]);
const records = ref<StrikeRecord[]>([]);

onMounted(async () => {
  try {
    const [
      summaryRows,
      monthlyRows,
      scenarioRows,
      phaseRows,
      sizeRows,
      altitudeRows,
      numRows,
      speciesRows,
      distanceRows,
      metricRows,
      finalMetricRows,
      featureRows,
      operatorRows,
      incidentRows,
      recordRows,
    ] = await Promise.all([
      loadCsv<SummaryRow>("/data/dashboard_summary.csv"),
      loadCsv<MonthlyTrendRow>("/data/monthly_damage_trend.csv"),
      loadCsv<AssessmentScenarioRow>("/data/assessment_scenarios.csv"),
      loadCsv<RiskRow>("/data/risk_by_phase.csv"),
      loadCsv<RiskRow>("/data/risk_by_size.csv"),
      loadCsv<RiskRow>("/data/risk_by_altitude_group.csv"),
      loadCsv<RiskRow>("/data/risk_by_num_struck.csv"),
      loadCsv<RiskRow>("/data/risk_by_species.csv"),
      loadCsv<RiskRow>("/data/risk_by_distance_group.csv"),
      loadCsv<MetricRow>("/data/metrics_table.csv"),
      loadCsv<MetricRow>("/data/final_model_metrics.csv"),
      loadCsv<FeatureRow>("/data/feature_importance.csv"),
      loadCsv<OperatorRow>("/data/operator_summary_top30.csv"),
      loadCsv<IncidentRow>("/data/operator_incident_queue.csv"),
      loadCsv<StrikeRecord>("/data/processed_modeling_data.csv"),
    ]);

    summary.value = summaryRows;
    monthly.value = monthlyRows;
    scenarios.value = scenarioRows;
    phaseRisk.value = phaseRows.filter((row) => row.min_count_pass === "True");
    sizeRisk.value = sizeRows.filter((row) => row.min_count_pass === "True");
    altitudeRisk.value = altitudeRows.filter((row) => row.min_count_pass === "True");
    numRisk.value = numRows.filter((row) => row.min_count_pass === "True");
    speciesRisk.value = speciesRows.filter((row) => row.min_count_pass === "True");
    distanceRisk.value = distanceRows.filter((row) => row.min_count_pass === "True");
    metrics.value = metricRows;
    finalMetrics.value = finalMetricRows;
    features.value = featureRows;
    operators.value = operatorRows;
    incidents.value = incidentRows;
    records.value = recordRows;
  } catch (err) {
    error.value = err instanceof Error ? err.message : "Unable to load dashboard data";
  } finally {
    loading.value = false;
  }
});

const appReady = computed(() => !loading.value && !error.value && summary.value[0] && finalMetrics.value[0] && operators.value[0]);
const pageTitle = computed(() =>
  activeTab.value === "analytics" ? "FAA Wildlife Strike Damage Analytics Overview" : "Wildlife Strike Damage Support System"
);
const pageSubtitle = computed(() =>
  activeTab.value === "analytics"
    ? "Damage-risk analysis summary from reported wildlife strike incidents"
    : "Post-strike damage review workflow from reported incident data"
);
</script>

<template>
  <div class="app-shell">
    <aside class="rail">
      <div class="brand">
        <strong>WSD</strong>
        <span>Damage Support System</span>
      </div>
      <button
        v-for="tab in tabs"
        :key="tab.id"
        type="button"
        class="nav-button"
        :class="{ active: activeTab === tab.id }"
        @click="activeTab = tab.id"
      >
        <b>{{ tab.index }}</b>
        <span>{{ tab.label }}</span>
      </button>
      <p class="rail-note">FAA wildlife strike reported incidents. Post-strike damage review, not live operations.</p>
    </aside>

    <main class="workspace">
      <header class="topbar" :class="{ compact: activeTab !== 'analytics' }">
        <div>
          <p class="eyebrow">FAA wildlife strike reported incident analysis</p>
          <h1>{{ pageTitle }}</h1>
          <p class="topbar-subtitle">{{ pageSubtitle }}</p>
        </div>
        <div class="mode-chip">reported incidents / decision-support demo</div>
      </header>

      <div v-if="loading" class="state-panel">Loading dashboard data...</div>
      <div v-else-if="error" class="state-panel error">{{ error }}</div>

      <template v-else-if="appReady">
        <AnalyticsOverview
          v-if="activeTab === 'analytics'"
          :summary="summary[0]"
          :monthly="monthly"
          :final-metric="finalMetrics[0]"
          :phase-risk="phaseRisk"
          :size-risk="sizeRisk"
          :altitude-risk="altitudeRisk"
          :species-risk="speciesRisk"
          :features="features"
          :metrics="metrics"
          :records="records"
        />
        <DamageAssessment v-else-if="activeTab === 'assessment'" :scenarios="scenarios" />
        <FlightPhaseExplorer
          v-else-if="activeTab === 'phase'"
          :phase-risk="phaseRisk"
          :altitude-risk="altitudeRisk"
          :distance-risk="distanceRisk"
        />
        <RiskFactorIntelligence
          v-else-if="activeTab === 'factors'"
          :size-risk="sizeRisk"
          :species-risk="speciesRisk"
          :altitude-risk="altitudeRisk"
          :num-risk="numRisk"
          :distance-risk="distanceRisk"
          :features="features"
        />
        <OperatorApplicationDemo
          v-else
          :operator="operators[0]"
          :incidents="incidents"
          :operator-phase="phaseRisk"
        />
      </template>
    </main>
  </div>
</template>
