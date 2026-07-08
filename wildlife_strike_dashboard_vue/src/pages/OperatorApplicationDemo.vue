<script setup lang="ts">
import { computed, ref } from "vue";
import AirportLayout from "../components/AirportLayout.vue";
import RiskGauge from "../components/RiskGauge.vue";
import type { IncidentRow, OperatorRow, RiskRow } from "../types";
import { fmtCount, fmtPct, riskColor } from "../utils/format";

const props = defineProps<{ operator: OperatorRow; incidents: IncidentRow[]; operatorPhase: RiskRow[] }>();
const selectedId = ref(props.incidents[0]?.report_id ?? "");
const selected = computed(() => props.incidents.find((row) => row.report_id === selectedId.value) ?? props.incidents[0]);
</script>

<template>
  <section class="operator-page">
    <aside class="queue-panel">
      <div class="panel-title">
        <div>
          <p class="eyebrow">Operator / airport application demo</p>
          <h2>Reported case review queue</h2>
        </div>
        <span class="mode-chip">{{ fmtCount(operator.total) }} reports</span>
      </div>
      <div class="queue-table" role="table" aria-label="Reported case review queue">
        <div class="queue-head" role="row">
          <span>ID</span>
          <span>Airport</span>
          <span>Phase</span>
          <span>Score</span>
        </div>
        <button
          v-for="item in incidents.slice(0, 24)"
          :key="item.report_id"
          type="button"
          class="queue-row"
          :class="{ active: selectedId === item.report_id }"
          role="row"
          @click="selectedId = item.report_id"
        >
          <span class="queue-id">{{ item.report_id.replace('SWA-RPT-', 'SWA-') }}</span>
          <strong>{{ item.AIRPORT }}</strong>
          <small>{{ item.PHASE_OF_FLIGHT }}</small>
          <b :style="{ color: riskColor(item.scenario_risk) }">{{ fmtPct(item.scenario_risk) }}</b>
          <em>{{ item.SIZE_CLEAN }} / {{ item.SPECIES }}</em>
        </button>
      </div>
    </aside>
    <article class="panel airport-demo">
      <div class="panel-title">
        <div>
          <p class="eyebrow">Surface scenario layer</p>
          <h2>{{ operator.OPERATOR }} reported-incident application view</h2>
        </div>
        <span class="mode-chip">highest reported operator example</span>
      </div>
      <AirportLayout :incidents="incidents" :selected-id="selectedId" @select="selectedId = $event" />
      <div class="application-readout">
        <section>
          <p class="eyebrow">Workflow handoff</p>
          <h3>Reported strike enters airport review queue</h3>
          <p>The model score is displayed as a triage layer before maintenance or engineering judgment.</p>
        </section>
        <section>
          <p class="eyebrow">Selected context</p>
          <h3>{{ selected?.AIRPORT }}</h3>
          <p>{{ selected?.PHASE_OF_FLIGHT }} / {{ selected?.ALTITUDE_GROUP }} / {{ selected?.SIZE_CLEAN }}</p>
        </section>
        <section>
          <p class="eyebrow">Surface layer use</p>
          <h3>Runway, approach, taxiway, and wildlife zones</h3>
          <p>Incidents are grouped as historical review points, not live aircraft positions.</p>
        </section>
      </div>
    </article>
    <aside class="panel assessment-panel">
      <p class="eyebrow">Selected report</p>
      <h2>{{ selected?.report_id }}</h2>
      <RiskGauge :value="selected?.scenario_risk ?? 0" label="Demo review score" />
      <dl class="detail-list">
        <div><dt>Airport</dt><dd>{{ selected?.AIRPORT }}</dd></div>
        <div><dt>Phase</dt><dd>{{ selected?.PHASE_OF_FLIGHT }}</dd></div>
        <div><dt>Altitude</dt><dd>{{ selected?.ALTITUDE_GROUP }}</dd></div>
        <div><dt>Wildlife</dt><dd>{{ selected?.SIZE_CLEAN }} / {{ selected?.SPECIES }}</dd></div>
        <div><dt>Operator reports</dt><dd>{{ fmtCount(operator.total) }} / {{ fmtPct(operator.damage_rate) }}</dd></div>
      </dl>
      <div class="operator-phase-strip">
        <span v-for="row in operatorPhase.slice(0, 4)" :key="row.category">
          <b>{{ row.category }}</b>
          {{ fmtPct(row.damage_rate) }}
        </span>
      </div>
      <div class="handoff-box">
        <p class="eyebrow">Decision-support handoff</p>
        <h3>Review before maintenance action</h3>
        <span>1. Confirm reported airport and phase</span>
        <span>2. Compare score against operator queue</span>
        <span>3. Send selected case to inspection review package</span>
      </div>
      <p class="fine-print">Highest reported operator is used only as a demo basis. This is not an airline safety ranking or operational exposure estimate.</p>
    </aside>
  </section>
</template>
