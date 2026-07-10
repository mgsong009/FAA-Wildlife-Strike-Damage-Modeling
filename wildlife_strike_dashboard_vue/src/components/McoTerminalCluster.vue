<script setup lang="ts">
import { computed } from "vue";
import referencePanelUrl from "../assets/mco-terminal-reference-panel.png";
import type { IncidentRow } from "../types";

const props = defineProps<{
  incidents: IncidentRow[];
  selectedId: string;
}>();

defineEmits<{ select: [id: string] }>();

const overlayMarkers = [
  { x: 70.5, y: 68.3 },
  { x: 71.5, y: 11.6 },
  { x: 83.0, y: 46.5 },
  { x: 29.6, y: 11.0 },
  { x: 27.8, y: 80.1 },
  { x: 60.4, y: 11.5 },
  { x: 19.0, y: 29.0 },
  { x: 31.5, y: 45.4 },
  { x: 16.0, y: 63.0 },
  { x: 83.0, y: 78.0 },
  { x: 65.0, y: 45.0 },
  { x: 37.0, y: 18.0 },
];

const visibleIncidents = computed(() => props.incidents.slice(0, overlayMarkers.length));

function markerFor(index: number) {
  return overlayMarkers[index % overlayMarkers.length];
}

function statusClass(item: IncidentRow): string {
  return `status-${(item.status ?? "NONE").toLowerCase()}`;
}
</script>

<template>
  <div class="mco-cluster-map reference-panel">
    <img :src="referencePanelUrl" alt="MCO terminal cluster overview reference diagram" />
    <button
      v-for="(item, index) in visibleIncidents"
      :key="item.report_id"
      type="button"
      class="mco-reference-hotspot"
      :class="[statusClass(item), { selected: item.report_id === selectedId }]"
      :style="{ left: `${markerFor(index).x}%`, top: `${markerFor(index).y}%` }"
      :aria-label="`${item.report_id} ${item.PHASE_OF_FLIGHT} ${item.surface_location}`"
      @click="$emit('select', item.report_id)"
    >
      <span>{{ item.report_id }}</span>
    </button>
  </div>
</template>
