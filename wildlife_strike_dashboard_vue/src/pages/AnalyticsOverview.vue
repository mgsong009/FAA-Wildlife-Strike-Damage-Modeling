<script setup lang="ts">
import { computed, ref } from "vue";
import DonutChart from "../components/DonutChart.vue";
import KpiCard from "../components/KpiCard.vue";
import SimpleBarChart from "../components/SimpleBarChart.vue";
import type { FeatureRow, MetricRow, MonthlyTrendRow, RiskRow, StrikeRecord, SummaryRow } from "../types";
import { fmtCount, fmtPct } from "../utils/format";

const props = defineProps<{
  summary: SummaryRow;
  monthly: MonthlyTrendRow[];
  finalMetric: MetricRow;
  phaseRisk: RiskRow[];
  sizeRisk: RiskRow[];
  altitudeRisk: RiskRow[];
  speciesRisk: RiskRow[];
  features: FeatureRow[];
  metrics: MetricRow[];
  records: StrikeRecord[];
}>();

const selectedPhase = ref("All");
const selectedAltitude = ref("All");
const selectedSize = ref("All");
const selectedDistance = ref("All");
const selectedNumberStruck = ref("All");
const selectedAircraftMass = ref("All");
const selectedSky = ref("All");

const phaseOptions = computed(() => ["All", ...uniqueValues("PHASE_OF_FLIGHT")]);
const altitudeOptions = computed(() => ["All", ...uniqueValues("ALTITUDE_GROUP")]);
const sizeOptions = computed(() => ["All", ...uniqueValues("SIZE_CLEAN")]);
const distanceOptions = computed(() => ["All", ...uniqueValues("DISTANCE_GROUP")]);
const numberStruckOptions = computed(() => ["All", ...uniqueValues("NUM_STRUCK")]);
const aircraftMassOptions = computed(() => ["All", ...uniqueValues("AC_MASS")]);
const skyOptions = computed(() => ["All", ...uniqueValues("SKY_CLEAN")]);

const filteredRecords = computed(() =>
  props.records.filter(
      (row) =>
      (selectedPhase.value === "All" || row.PHASE_OF_FLIGHT === selectedPhase.value) &&
      (selectedAltitude.value === "All" || row.ALTITUDE_GROUP === selectedAltitude.value) &&
      (selectedSize.value === "All" || row.SIZE_CLEAN === selectedSize.value) &&
      (selectedDistance.value === "All" || row.DISTANCE_GROUP === selectedDistance.value) &&
      (selectedNumberStruck.value === "All" || row.NUM_STRUCK === selectedNumberStruck.value) &&
      (selectedAircraftMass.value === "All" || row.AC_MASS === selectedAircraftMass.value) &&
      (selectedSky.value === "All" || row.SKY_CLEAN === selectedSky.value)
  )
);

const filteredSummary = computed(() => {
  const total = filteredRecords.value.length;
  const damaged = filteredRecords.value.reduce((sum, row) => sum + Number(row.Damage_Binary || 0), 0);
  return { total, damaged, damageRate: total ? damaged / total : 0 };
});

const filteredMonthly = computed(() => groupByMonth(filteredRecords.value));
const monthMax = computed(() => Math.max(...filteredMonthly.value.map((row) => row.total_count), 1));
const phaseBars = computed(() =>
  groupRate(filteredRecords.value, "PHASE_OF_FLIGHT").map((row) => ({ label: row.category, value: row.damage_rate, count: row.total_count }))
);
const sizeBars = computed(() =>
  groupRate(filteredRecords.value, "SIZE_CLEAN").map((row) => ({ label: row.category, value: row.damage_rate, count: row.total_count }))
);
const altitudeBars = computed(() =>
  groupRate(filteredRecords.value, "ALTITUDE_GROUP").map((row) => ({ label: row.category, value: row.damage_rate, count: row.total_count }))
);
const speciesBars = props.speciesRisk.slice(0, 8).map((row) => ({ label: row.category, value: row.damage_rate, count: row.total_count }));
const featureBars = props.features.slice(0, 10).map((row) => ({ label: cleanFeature(row.feature), value: row.importance }));
const modelBars = props.metrics.filter((row) => row.split === "test").map((row) => ({ label: row.model_name, value: row.f1 }));
const selectedFilters = computed(() =>
  [
    ["Phase", selectedPhase.value],
    ["Altitude", selectedAltitude.value],
    ["Distance", selectedDistance.value],
    ["Wildlife", selectedSize.value],
    ["Struck", selectedNumberStruck.value],
    ["Mass", selectedAircraftMass.value],
    ["Sky", selectedSky.value],
  ].filter(([, value]) => value !== "All")
);

function cleanFeature(value: string): string {
  return value
    .replace("SIZE_CLEAN", "Wildlife size")
    .replace("AC_MASS", "Aircraft mass")
    .replace("NUM_STRUCK", "Number struck")
    .replace("FAAREGION", "FAA region")
    .replace("PHASE_OF_FLIGHT", "Flight phase")
    .replace("ALTITUDE_GROUP", "Altitude group")
    .replace("DISTANCE_GROUP", "Airport distance")
    .replace(/_/g, " ");
}

function uniqueValues(key: keyof StrikeRecord): string[] {
  return Array.from(new Set(props.records.map((row) => String(row[key] || "Unknown")))).sort();
}

function groupByMonth(rows: StrikeRecord[]): MonthlyTrendRow[] {
  const buckets = new Map<number, { total_count: number; damage_count: number }>();
  for (let month = 1; month <= 12; month += 1) {
    buckets.set(month, { total_count: 0, damage_count: 0 });
  }
  rows.forEach((row) => {
    const month = Number(row.INCIDENT_MONTH);
    const bucket = buckets.get(month) ?? { total_count: 0, damage_count: 0 };
    bucket.total_count += 1;
    bucket.damage_count += Number(row.Damage_Binary || 0);
    buckets.set(month, bucket);
  });
  return Array.from(buckets.entries()).map(([INCIDENT_MONTH, bucket]) => ({
    INCIDENT_MONTH,
    total_count: bucket.total_count,
    damage_count: bucket.damage_count,
    damage_rate: bucket.total_count ? bucket.damage_count / bucket.total_count : 0,
  }));
}

function groupRate(rows: StrikeRecord[], key: keyof StrikeRecord): RiskRow[] {
  const buckets = new Map<string, { total_count: number; damage_count: number }>();
  rows.forEach((row) => {
    const category = String(row[key] || "Unknown");
    const bucket = buckets.get(category) ?? { total_count: 0, damage_count: 0 };
    bucket.total_count += 1;
    bucket.damage_count += Number(row.Damage_Binary || 0);
    buckets.set(category, bucket);
  });
  return Array.from(buckets.entries())
    .map(([category, bucket]) => ({
      category,
      total_count: bucket.total_count,
      damage_count: bucket.damage_count,
      damage_rate: bucket.total_count ? bucket.damage_count / bucket.total_count : 0,
      overall_damage_rate: filteredSummary.value.damageRate,
      risk_lift: filteredSummary.value.damageRate ? bucket.damage_count / bucket.total_count / filteredSummary.value.damageRate : 0,
      min_count_pass: "True",
    }))
    .sort((a, b) => b.damage_rate - a.damage_rate)
    .slice(0, 9);
}
</script>

<template>
  <section class="analytics-page">
    <aside class="filter-board">
      <p class="eyebrow">Analytics controls</p>
      <h2>Reported incident lens</h2>
      <div class="filter-group">
        <label class="filter-select">
          Phase of flight
          <select v-model="selectedPhase"><option v-for="option in phaseOptions" :key="option">{{ option }}</option></select>
        </label>
        <label class="filter-select">
          Altitude group
          <select v-model="selectedAltitude"><option v-for="option in altitudeOptions" :key="option">{{ option }}</option></select>
        </label>
        <label class="filter-select">
          Airport distance
          <select v-model="selectedDistance"><option v-for="option in distanceOptions" :key="option">{{ option }}</option></select>
        </label>
        <label class="filter-select">
          Wildlife size
          <select v-model="selectedSize"><option v-for="option in sizeOptions" :key="option">{{ option }}</option></select>
        </label>
        <label class="filter-select">
          Number struck
          <select v-model="selectedNumberStruck"><option v-for="option in numberStruckOptions" :key="option">{{ option }}</option></select>
        </label>
        <label class="filter-select">
          Aircraft mass
          <select v-model="selectedAircraftMass"><option v-for="option in aircraftMassOptions" :key="option">{{ option }}</option></select>
        </label>
        <label class="filter-select">
          Sky condition
          <select v-model="selectedSky"><option v-for="option in skyOptions" :key="option">{{ option }}</option></select>
        </label>
      </div>
      <p class="fine-print">Interactive BI view. KPI and charts update from selected reported-incident filters.</p>
      <div class="filter-context">
        <span>
          <small>Current lens</small>
          <b>{{ selectedFilters.length ? `${selectedFilters.length} active filters` : "All reported incidents" }}</b>
        </span>
        <span v-for="[label, value] in selectedFilters" :key="label">
          <small>{{ label }}</small>
          <b>{{ value }}</b>
        </span>
      </div>
    </aside>

    <div class="analytics-main">
      <div class="kpi-strip compact">
        <KpiCard label="Total Reports" :value="fmtCount(filteredSummary.total)" detail="reported incident records" tone="blue" />
        <KpiCard label="Damaged Cases" :value="fmtCount(filteredSummary.damaged)" detail="target class = damaged" tone="amber" />
        <KpiCard label="Overall Damage Rate" :value="fmtPct(filteredSummary.damageRate, 2)" detail="within selected reports" tone="green" />
        <KpiCard label="Final Model" :value="summary.final_model" detail="selected validation model" tone="neutral" />
        <KpiCard label="Threshold" :value="String(summary.final_threshold)" detail="damage review cut point" tone="neutral" />
      </div>

      <div class="overview-grid">
        <article class="panel span-2">
          <div class="panel-title"><h2>Monthly damage rate and report volume</h2><span class="mode-chip">12 months</span></div>
          <div class="month-chart">
            <div v-for="row in filteredMonthly" :key="row.INCIDENT_MONTH" class="month-col">
              <i :style="{ height: `${Math.max((row.total_count / monthMax) * 150, 8)}px` }"></i>
              <b>{{ fmtPct(row.damage_rate, 0) }}</b>
              <span>{{ row.INCIDENT_MONTH }}</span>
            </div>
          </div>
        </article>
        <article class="panel"><h2>Class balance</h2><DonutChart :value="filteredSummary.damageRate" label="damaged reports" tone="amber" /></article>
        <article class="panel">
          <h2>Model comparison</h2>
          <SimpleBarChart :rows="modelBars" />
          <div class="model-note">
            <b>Selection note</b>
            <span>Decision Tree is kept as the demo model because its rule path is easier to explain in an inspection-support workflow, even though Random Forest has a slightly higher F1.</span>
          </div>
        </article>
        <article class="panel"><h2>Flight phase damage rate</h2><SimpleBarChart :rows="phaseBars" /></article>
        <article class="panel"><h2>Wildlife size damage rate</h2><SimpleBarChart :rows="sizeBars" /></article>
        <article class="panel"><h2>Altitude group damage rate</h2><SimpleBarChart :rows="altitudeBars" /></article>
        <article class="panel"><h2>Feature importance top 10</h2><SimpleBarChart :rows="featureBars" value-label="number" /></article>
        <article class="panel span-2"><h2>Top species damage rate</h2><SimpleBarChart :rows="speciesBars" /></article>
        <article class="panel">
          <h2>Confusion matrix summary</h2>
          <div class="metric-stack">
            <span><b>Precision</b>{{ fmtPct(finalMetric.precision, 1) }}</span>
            <span><b>Recall</b>{{ fmtPct(finalMetric.recall, 1) }}</span>
            <span><b>F1 score</b>{{ fmtPct(finalMetric.f1, 1) }}</span>
          </div>
          <p class="fine-print">Accuracy is not the main read because damaged reports are rare.</p>
        </article>
        <article class="panel insight-panel">
          <h2>Analytical readout</h2>
          <p>Large wildlife, high-altitude reports, and climb-phase events show materially higher damage rates than the overall baseline.</p>
          <p>Use this page as the evidence layer for the operational workflow pages.</p>
        </article>
      </div>
    </div>
  </section>
</template>
