<script setup lang="ts">
import { computed, ref, watch } from "vue";
import McoIncidentDetail from "../components/McoIncidentDetail.vue";
import McoIncidentQueue from "../components/McoIncidentQueue.vue";
import McoKpiStrip from "../components/McoKpiStrip.vue";
import McoMonthlyStackedChart from "../components/McoMonthlyStackedChart.vue";
import McoSpeciesDonut from "../components/McoSpeciesDonut.vue";
import McoTerminalCluster from "../components/McoTerminalCluster.vue";
import type { AirportConsoleSummaryRow, IncidentRow, McoMonthlyStatusRow, McoSpeciesRow } from "../types";

const props = defineProps<{
  summary: AirportConsoleSummaryRow;
  incidents: IncidentRow[];
  monthlyStatus: McoMonthlyStatusRow[];
  species: McoSpeciesRow[];
}>();

const selectedId = ref(props.incidents[0]?.report_id ?? "");
const selected = computed(() => props.incidents.find((row) => row.report_id === selectedId.value) ?? props.incidents[0]);
const queueIncidents = computed(() => {
  const weighted = [...props.incidents].sort((a, b) => {
    const statusWeight = (row: IncidentRow) => (row.status === "DAMAGED" ? 3 : row.status === "POSSIBLE" ? 2 : 1);
    return statusWeight(b) - statusWeight(a) || Number(b.scenario_risk) - Number(a.scenario_risk);
  });
  return weighted.slice(0, 35);
});

watch(
  () => props.incidents,
  (rows) => {
    if (!selectedId.value && rows[0]) selectedId.value = rows[0].report_id;
  }
);
</script>

<template>
  <section class="mco-console-page redesigned">
    <McoKpiStrip :summary="summary" />

    <div class="mco-ops-grid">
      <McoIncidentQueue :incidents="queueIncidents" :selected-id="selectedId" @select="selectedId = $event" />

      <article class="mco-console-card mco-map-shell">
        <McoTerminalCluster :incidents="queueIncidents" :selected-id="selectedId" @select="selectedId = $event" />
      </article>

      <McoIncidentDetail :incident="selected" />
    </div>

    <div class="mco-bottom-grid">
      <McoMonthlyStackedChart :rows="monthlyStatus" />
      <McoSpeciesDonut :rows="species" />
    </div>
  </section>
</template>
