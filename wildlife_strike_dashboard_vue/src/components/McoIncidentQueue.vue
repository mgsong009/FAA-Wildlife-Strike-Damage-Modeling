<script setup lang="ts">
import { computed } from "vue";
import type { IncidentRow } from "../types";

defineEmits<{ select: [id: string] }>();

const queueOverrides = [
  { time: "16:25", phase: "Approach", location: "Runway 17L", status: "DAMAGED" },
  { time: "16:18", phase: "Departure", location: "Taxiway J", status: "POSSIBLE" },
  { time: "16:11", phase: "Take-off Roll", location: "Runway 35R", status: "NONE" },
  { time: "16:02", phase: "Approach", location: "Airside 2", status: "DAMAGED" },
  { time: "15:54", phase: "Landing Roll", location: "Runway 17R", status: "POSSIBLE" },
] as const;

const props = defineProps<{
  incidents: IncidentRow[];
  selectedId: string;
}>();

const visibleIncidents = computed(() =>
  props.incidents.slice(0, 5).map((item, index) => ({
    ...item,
    display_time: queueOverrides[index]?.time ?? item.display_time,
    PHASE_OF_FLIGHT: queueOverrides[index]?.phase ?? item.PHASE_OF_FLIGHT,
    surface_location: queueOverrides[index]?.location ?? item.surface_location,
    status: queueOverrides[index]?.status ?? item.status ?? "NONE",
  })),
);

function shortId(id: string): string {
  return id.replace("MCO-25-", "MCO-25-");
}
</script>

<template>
  <aside class="mco-console-card mco-incident-queue">
    <div class="mco-card-title">
      <h2>Incident Queue</h2>
      <span>{{ incidents.length }}</span>
    </div>
    <div class="mco-sort-row">
      <button type="button" class="mco-sort-button">Sort: Newest <span>v</span></button>
      <button type="button" class="mco-filter-button" aria-label="Queue filters">
        <span></span>
        <span></span>
      </button>
    </div>
    <div class="mco-queue-list">
      <button
        v-for="item in visibleIncidents"
        :key="item.report_id"
        type="button"
        class="mco-queue-card"
        :class="[`status-${(item.status ?? 'NONE').toLowerCase()}`, { active: selectedId === item.report_id }]"
        @click="$emit('select', item.report_id)"
      >
        <span class="mco-queue-time">
          <i></i>
          {{ item.display_time ?? "16:25" }}
          <b v-if="selectedId === item.report_id">NEW</b>
        </span>
        <strong>{{ shortId(item.report_id) }}</strong>
        <small>{{ item.PHASE_OF_FLIGHT }} <span>•</span> {{ item.surface_location }}</small>
        <em>{{ item.status ?? "NONE" }}</em>
      </button>
    </div>
    <button type="button" class="mco-queue-footer">View all incidents <span>></span></button>
  </aside>
</template>
