<script setup lang="ts">
import { computed, ref } from "vue";
import RiskGauge from "../components/RiskGauge.vue";
import type { AssessmentScenarioRow } from "../types";
import { fmtPct, riskColor, riskLevel } from "../utils/format";

const props = defineProps<{ scenarios: AssessmentScenarioRow[] }>();
const selectedId = ref(props.scenarios[0]?.scenario_id ?? "");
const selected = computed(() => props.scenarios.find((row) => row.scenario_id === selectedId.value) ?? props.scenarios[0]);
const drivers = computed(() => [
  { label: "Wildlife size", name: selected.value?.SIZE_CLEAN, value: selected.value?.size_rate ?? 0 },
  { label: "Flight phase", name: selected.value?.PHASE_OF_FLIGHT, value: selected.value?.phase_rate ?? 0 },
  { label: "Altitude band", name: selected.value?.ALTITUDE_GROUP, value: selected.value?.altitude_rate ?? 0 },
  { label: "Airport distance", name: selected.value?.DISTANCE_GROUP, value: selected.value?.distance_rate ?? 0 },
]);
const priorityLabel = computed(() =>
  riskLevel(selected.value?.risk_score ?? 0) === "Critical" ? "Elevate for inspection review" : "Routine review"
);
</script>

<template>
  <section class="assessment-page">
    <aside class="scenario-list panel">
      <p class="eyebrow">Post-strike cases</p>
      <h2>Assessment queue</h2>
      <button
        v-for="row in scenarios.slice(0, 18)"
        :key="row.scenario_id"
        type="button"
        class="scenario-row"
        :class="{ active: selectedId === row.scenario_id }"
        @click="selectedId = row.scenario_id"
      >
        <span>{{ row.scenario_id }}</span>
        <strong>{{ row.PHASE_OF_FLIGHT }} / {{ row.SIZE_CLEAN }}</strong>
        <small>{{ row.ALTITUDE_GROUP }} / {{ row.DISTANCE_GROUP }}</small>
        <b :style="{ color: riskColor(row.risk_score) }">{{ fmtPct(row.risk_score) }}</b>
      </button>
    </aside>

    <article class="assessment-core panel">
      <div class="assessment-header">
        <div>
          <p class="eyebrow">Post-strike damage assessment</p>
          <h2>Should this reported strike be elevated for inspection review?</h2>
        </div>
        <span
          class="risk-badge"
          :style="{ color: riskColor(selected?.risk_score ?? 0), borderColor: riskColor(selected?.risk_score ?? 0) }"
        >
          {{ riskLevel(selected?.risk_score ?? 0) }}
        </span>
      </div>

      <div class="selected-report-strip">
        <span>
          <small>Selected report</small>
          <b>{{ selected?.scenario_id }}</b>
        </span>
        <span>
          <small>Phase</small>
          <b>{{ selected?.PHASE_OF_FLIGHT }}</b>
        </span>
        <span>
          <small>Altitude</small>
          <b>{{ selected?.ALTITUDE_GROUP }}</b>
        </span>
        <span>
          <small>Wildlife</small>
          <b>{{ selected?.SIZE_CLEAN }}</b>
        </span>
      </div>

      <div class="assessment-decision">
        <RiskGauge :value="selected?.risk_score ?? 0" label="Damage review score" />
        <div class="decision-panel">
          <p class="eyebrow">Review recommendation</p>
          <h3>{{ priorityLabel }}</h3>
          <strong>{{ selected?.recommendation }}</strong>
          <p>This score supports inspection priority after a reported strike. It is not a maintenance clearance decision.</p>
          <div class="score-basis compact-strip">
            <b>Dashboard review score</b>
            <span>Historical condition rates combined for triage support before engineering or maintenance judgment.</span>
          </div>
        </div>
      </div>

      <section class="score-explain">
        <div class="panel-title">
          <div>
            <p class="eyebrow">Why this score</p>
            <h2>Selected condition evidence</h2>
          </div>
          <span class="mode-chip">historical reported incidents</span>
        </div>
        <div class="evidence-tiles">
          <span v-for="driver in drivers" :key="driver.label">
            <small>{{ driver.label }}</small>
            <b>{{ driver.name }}</b>
            <i :style="{ width: `${Math.max(driver.value * 100, 8)}%`, background: riskColor(driver.value) }"></i>
            <strong>{{ fmtPct(driver.value) }}</strong>
          </span>
        </div>
      </section>

      <dl class="detail-list compact-details">
        <div><dt>Distance</dt><dd>{{ selected?.DISTANCE_GROUP }}</dd></div>
        <div><dt>Species</dt><dd>{{ selected?.SPECIES }}</dd></div>
        <div><dt>Aircraft mass</dt><dd>{{ selected?.AC_MASS }}</dd></div>
        <div><dt>Sky condition</dt><dd>{{ selected?.SKY_CLEAN }}</dd></div>
      </dl>

      <section class="action-lane">
        <div>
          <p class="eyebrow">Review action</p>
          <h3>Queue for maintenance review package</h3>
          <p>Attach reported conditions, score basis, and evidence tiles before an engineering decision is made.</p>
        </div>
        <ol>
          <li>Confirm reported phase and altitude band</li>
          <li>Check wildlife size and species description</li>
          <li>Route high-score cases to priority inspection review</li>
        </ol>
      </section>
    </article>

    <aside class="panel driver-panel">
      <p class="eyebrow">Review boundary</p>
      <h2>How to read this</h2>
      <div class="driver-note">
        This page ranks reported strike cases for review attention. It does not replace engineering inspection, maintenance sign-off, or live causal diagnosis.
      </div>
      <div v-for="driver in drivers" :key="driver.label" class="driver-row">
        <span>{{ driver.label }}</span>
        <strong>{{ driver.name }}</strong>
        <i :style="{ width: `${Math.max(driver.value * 260, 10)}px`, background: riskColor(driver.value) }"></i>
        <b>{{ fmtPct(driver.value) }}</b>
      </div>
    </aside>
  </section>
</template>
