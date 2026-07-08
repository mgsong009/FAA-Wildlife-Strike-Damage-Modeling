<script setup lang="ts">
import { computed, ref } from "vue";
import FlightPhaseProfile from "../components/FlightPhaseProfile.vue";
import SimpleBarChart from "../components/SimpleBarChart.vue";
import type { RiskRow } from "../types";
import { fmtCount, fmtLift, fmtPct, riskColor } from "../utils/format";

const props = defineProps<{ phaseRisk: RiskRow[]; altitudeRisk: RiskRow[]; distanceRisk: RiskRow[] }>();
const phaseSequence = ["Take-off Run", "Climb", "Descent", "Approach", "Landing Roll", "Taxi"];
const orderedPhaseProfile = computed(() =>
  phaseSequence
    .map((phase) => props.phaseRisk.find((row) => row.category === phase))
    .filter((row): row is RiskRow => Boolean(row))
);
const selectedPhase = ref(orderedPhaseProfile.value[0]?.category ?? props.phaseRisk[0]?.category ?? "");
const selected = computed(() => props.phaseRisk.find((row) => row.category === selectedPhase.value) ?? props.phaseRisk[0]);
const phaseBars = computed(() => props.phaseRisk.map((row) => ({ label: row.category, value: row.damage_rate, count: row.total_count })));
const altitudeBars = computed(() => props.altitudeRisk.map((row) => ({ label: row.category, value: row.damage_rate, count: row.total_count })));
const distanceBars = computed(() => props.distanceRisk.map((row) => ({ label: row.category, value: row.damage_rate, count: row.total_count })));
const selectedIndex = computed(() => orderedPhaseProfile.value.findIndex((row) => row.category === selectedPhase.value) + 1);
const selectedTrendText = computed(() => {
  const lift = selected.value?.risk_lift ?? 0;
  if (lift >= 1.4) return "Above baseline review attention";
  if (lift >= 1) return "Near baseline with condition-dependent variation";
  return "Below overall reported damage baseline";
});
</script>

<template>
  <section class="phase-page">
    <article class="panel phase-map">
      <div class="panel-title"><div><p class="eyebrow">Historical phase profile</p><h2>Damage rate across flight phase</h2></div><span class="mode-chip">not live tracking</span></div>
      <FlightPhaseProfile :rows="orderedPhaseProfile" :selected="selectedPhase" />
      <div class="phase-buttons">
        <button v-for="row in orderedPhaseProfile" :key="row.category" type="button" :class="{ active: selectedPhase === row.category }" @click="selectedPhase = row.category">
          {{ row.category }}
        </button>
      </div>
    </article>
    <aside class="panel">
      <p class="eyebrow">Selected phase readout</p>
      <h2>{{ selected?.category }}</h2>
      <div class="phase-readout">
        <span>
          <small>Damage rate</small>
          <b :style="{ color: riskColor(selected?.damage_rate ?? 0) }">{{ fmtPct(selected?.damage_rate) }}</b>
        </span>
        <span>
          <small>Risk lift</small>
          <b>{{ fmtLift(selected?.risk_lift) }}</b>
        </span>
        <span>
          <small>Reports</small>
          <b>{{ fmtCount(selected?.total_count) }}</b>
        </span>
        <span>
          <small>Sequence</small>
          <b>{{ selectedIndex }} / {{ orderedPhaseProfile.length }}</b>
        </span>
      </div>
      <div class="phase-status" :style="{ borderColor: riskColor(selected?.damage_rate ?? 0) }">
        <b>{{ selectedTrendText }}</b>
        <p>Historical reported incidents only. Use this view to explain where damage rates differ across the flight profile.</p>
      </div>
      <div class="phase-context">
        <span>
          <small>Operational question</small>
          <b>Which phase should receive more review attention?</b>
        </span>
        <span>
          <small>How to use</small>
          <b>Compare phase rate with altitude and airport-distance patterns below.</b>
        </span>
        <span>
          <small>Boundary</small>
          <b>This is not a flight path tracker or live hazard display.</b>
        </span>
      </div>
    </aside>
    <article class="panel"><h2>Phase ranking</h2><SimpleBarChart :rows="phaseBars" /></article>
    <article class="panel"><h2>Altitude groups</h2><SimpleBarChart :rows="altitudeBars" /></article>
    <article class="panel"><h2>Airport distance</h2><SimpleBarChart :rows="distanceBars" /></article>
  </section>
</template>
