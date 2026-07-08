<script setup lang="ts">
import { computed } from "vue";
import SimpleBarChart from "../components/SimpleBarChart.vue";
import type { FeatureRow, RiskRow } from "../types";
import { fmtCount, fmtPct, riskColor } from "../utils/format";

const props = defineProps<{
  sizeRisk: RiskRow[];
  speciesRisk: RiskRow[];
  altitudeRisk: RiskRow[];
  numRisk: RiskRow[];
  distanceRisk: RiskRow[];
  features: FeatureRow[];
}>();

type MatrixRow = RiskRow & { group: string };

const matrixRows = computed<MatrixRow[]>(() =>
  [
    ...props.sizeRisk.map((row) => ({ ...row, group: "Size" })),
    ...props.altitudeRisk.map((row) => ({ ...row, group: "Altitude" })),
    ...props.distanceRisk.map((row) => ({ ...row, group: "Distance" })),
    ...props.numRisk.map((row) => ({ ...row, group: "Number struck" })),
    ...props.speciesRisk.slice(0, 8).map((row) => ({ ...row, group: "Species" })),
  ]
    .filter((row) => row.total_count >= 50)
    .sort((a, b) => b.damage_rate - a.damage_rate)
);

const maxCount = computed(() => Math.max(...matrixRows.value.map((row) => row.total_count), 1));
const maxRate = computed(() => Math.max(...matrixRows.value.map((row) => row.damage_rate), 0.001));
const topMatrixRows = computed(() => matrixRows.value.slice(0, 6));
const matrixDisplayRows = computed(() => {
  const selected = [...matrixRows.value.slice(0, 3)];
  matrixRows.value
    .filter((row) => row.total_count > 10000)
    .slice(0, 4)
    .forEach((row) => {
      if (!selected.some((item) => item.group === row.group && item.category === row.category)) {
        selected.push(row);
      }
    });
  return selected;
});
const keyDrivers = computed(() => [
  {
    label: "Primary severity driver",
    value: props.sizeRisk[0]?.category ?? "Unknown",
    detail: `${fmtPct(props.sizeRisk[0]?.damage_rate ?? 0)} damage rate across ${fmtCount(props.sizeRisk[0]?.total_count ?? 0)} reports`,
  },
  {
    label: "Most exposed altitude band",
    value: props.altitudeRisk[0]?.category ?? "Unknown",
    detail: `${fmtPct(props.altitudeRisk[0]?.damage_rate ?? 0)} damage rate`,
  },
  {
    label: "Model top feature",
    value: cleanFeature(props.features[0]?.feature ?? "Unknown"),
    detail: `${(props.features[0]?.importance ?? 0).toFixed(2)} relative importance`,
  },
]);

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

function matrixX(count: number): number {
  const scale = Math.log10(count + 1) / Math.log10(maxCount.value + 1);
  return 70 + scale * 470;
}

function matrixY(rate: number): number {
  return 302 - (rate / maxRate.value) * 238;
}

function matrixRadius(row: MatrixRow): number {
  return 6 + Math.min(row.risk_lift * 3, 13);
}
</script>

<template>
  <section class="factor-page">
    <article class="driver-command-panel">
      <p class="eyebrow">Wildlife & aircraft risk factors</p>
      <h2>Which conditions push reported strike damage higher?</h2>
      <div class="driver-cards">
        <span v-for="driver in keyDrivers" :key="driver.label">
          <small>{{ driver.label }}</small>
          <b>{{ driver.value }}</b>
          <em>{{ driver.detail }}</em>
        </span>
      </div>
      <div class="interpretation-stack">
        <span>
          <b>Severity read</b>
          Large wildlife is treated as a severity driver because its reported damage rate is far above the dataset baseline.
        </span>
        <span>
          <b>Frequency read</b>
          High-volume conditions are not always the highest-damage conditions, so volume and severity are shown separately.
        </span>
        <span>
          <b>Model read</b>
          Feature importance explains model split behavior; it does not prove causal wildlife occurrence risk.
        </span>
        <span>
          <b>Operational use</b>
          Use this page to explain why a case receives a higher review score before showing the assessment queue.
        </span>
      </div>
      <div class="factor-guardrails">
        <span>
          <small>Best read</small>
          <b>Damage severity after a reported strike</b>
        </span>
        <span>
          <small>Do not read as</small>
          <b>Wildlife occurrence probability or airport safety ranking</b>
        </span>
      </div>
      <p class="fine-print">Interpretation layer for post-strike review. These are reported-incident patterns, not wildlife occurrence probabilities.</p>
    </article>
    <article class="wide-panel matrix-panel">
      <div class="panel-title">
        <div>
          <p class="eyebrow">Frequency vs severity</p>
          <h2>Reported volume and damage rate do not always move together.</h2>
        </div>
        <span class="mode-chip">bubble size = risk lift</span>
      </div>
      <svg class="severity-matrix" viewBox="0 0 620 360" role="img" aria-label="Frequency and damage rate matrix">
        <line class="matrix-grid" x1="70" y1="64" x2="70" y2="302" />
        <line class="matrix-grid" x1="70" y1="302" x2="540" y2="302" />
        <line class="matrix-guide" x1="305" y1="64" x2="305" y2="302" />
        <line class="matrix-guide" x1="70" y1="183" x2="540" y2="183" />
        <text x="72" y="38" class="matrix-axis">Higher damage rate</text>
        <text x="372" y="334" class="matrix-axis">More reported incidents</text>
        <text x="92" y="174" class="quadrant-label">higher severity</text>
        <text x="382" y="284" class="quadrant-label">higher volume</text>
        <g v-for="row in matrixDisplayRows" :key="`${row.group}-${row.category}`">
          <circle
            class="matrix-dot"
            :cx="matrixX(row.total_count)"
            :cy="matrixY(row.damage_rate)"
            :r="matrixRadius(row)"
            :fill="riskColor(row.damage_rate)"
          />
        </g>
        <g v-for="(row, index) in topMatrixRows.slice(0, 3)" :key="`${row.group}-${row.category}-label`">
          <line
            class="matrix-label-line"
            :x1="matrixX(row.total_count)"
            :y1="matrixY(row.damage_rate)"
            x2="416"
            :y2="92 + index * 44"
          />
          <text
            class="matrix-label"
            x="424"
            :y="96 + index * 44"
          >
            {{ row.group }} / {{ row.category }}
          </text>
        </g>
      </svg>
      <div class="matrix-summary">
        <span v-for="row in topMatrixRows.slice(0, 3)" :key="`${row.group}-${row.category}-summary`">
          <b>{{ row.category }}</b>
          {{ fmtPct(row.damage_rate) }} damage / {{ fmtCount(row.total_count) }} reports
        </span>
      </div>
    </article>
    <article class="panel"><h2>Wildlife size</h2><SimpleBarChart :rows="sizeRisk.map(row => ({ label: row.category, value: row.damage_rate, count: row.total_count }))" /></article>
    <article class="panel"><h2>Number struck</h2><SimpleBarChart :rows="numRisk.map(row => ({ label: row.category || 'Unknown', value: row.damage_rate, count: row.total_count }))" /></article>
    <article class="panel"><h2>Altitude</h2><SimpleBarChart :rows="altitudeRisk.map(row => ({ label: row.category, value: row.damage_rate, count: row.total_count }))" /></article>
    <article class="panel"><h2>Distance</h2><SimpleBarChart :rows="distanceRisk.map(row => ({ label: row.category, value: row.damage_rate, count: row.total_count }))" /></article>
    <article class="wide-panel"><h2>Species by reported damage rate</h2><SimpleBarChart :rows="speciesRisk.slice(0, 10).map(row => ({ label: row.category, value: row.damage_rate, count: row.total_count }))" /></article>
    <article class="wide-panel"><h2>Model feature importance</h2><SimpleBarChart :rows="features.slice(0, 10).map(row => ({ label: cleanFeature(row.feature), value: row.importance }))" value-label="number" /></article>
  </section>
</template>
