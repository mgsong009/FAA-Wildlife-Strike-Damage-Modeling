<script setup lang="ts">
import { computed } from "vue";
import type { IncidentRow } from "../types";
import { fmtPct, riskColor } from "../utils/format";

const props = defineProps<{
  incidents: IncidentRow[];
  selectedId: string;
}>();

defineEmits<{ select: [id: string] }>();

const selectedIncident = computed(() => props.incidents.find((item) => item.report_id === props.selectedId));

function markerX(index: number): number {
  return [168, 266, 366, 506, 636, 774, 852, 226, 574, 718][index % 10];
}

function markerY(index: number): number {
  return [186, 226, 176, 246, 184, 224, 190, 304, 304, 302][index % 10];
}

function selectedIndex(): number {
  return Math.max(
    props.incidents.slice(0, 10).findIndex((item) => item.report_id === props.selectedId),
    0
  );
}
</script>

<template>
  <svg class="airport-layout" viewBox="0 0 1000 500" role="img" aria-label="Airport application layout">
    <rect x="76" y="70" width="840" height="350" class="airport-boundary" />
    <rect x="112" y="104" width="210" height="56" class="review-zone" />
    <rect x="672" y="104" width="204" height="56" class="review-zone red" />
    <path class="approach-path" d="M70 214 C180 178 282 174 392 198 M930 214 C822 178 734 176 612 198" />
    <rect x="138" y="196" width="730" height="34" class="runway" />
    <rect x="152" y="209" width="700" height="8" class="runway-centerline" />
    <path class="runway-arrow" d="M820 190 L858 213 L820 236" />
    <path class="runway-arrow left" d="M186 190 L148 213 L186 236" />
    <rect x="222" y="286" width="558" height="22" class="taxiway" />
    <rect x="398" y="336" width="206" height="48" class="terminal" />
    <circle cx="206" cy="132" r="34" class="wildlife-zone" />
    <circle cx="780" cy="132" r="38" class="wildlife-zone red-zone" />

    <text x="454" y="190" class="layout-label">RWY 09 / 27</text>
    <text x="456" y="278" class="layout-label">PARALLEL TAXIWAY</text>
    <text x="456" y="365" class="layout-label">TERMINAL APRON</text>
    <text x="130" y="138" class="layout-label accent">WILDLIFE REVIEW ZONE A</text>
    <text x="690" y="138" class="layout-label accent">WILDLIFE REVIEW ZONE B</text>
    <text x="70" y="174" class="layout-label muted">APPROACH CORRIDOR</text>
    <text x="724" y="174" class="layout-label muted">APPROACH CORRIDOR</text>

    <g v-for="(item, index) in incidents.slice(0, 10)" :key="item.report_id">
      <circle
        :cx="markerX(index)"
        :cy="markerY(index)"
        :r="selectedId === item.report_id ? 12 : 7"
        :fill="riskColor(item.scenario_risk)"
        class="layout-marker"
        :class="{ selected: selectedId === item.report_id }"
        @click="$emit('select', item.report_id)"
      />
    </g>

    <g v-if="selectedIncident" class="layout-callout">
      <path
        class="selected-trail"
        :d="`M${markerX(selectedIndex()) + 10} ${markerY(selectedIndex()) - 10} L${markerX(selectedIndex()) + 70} ${markerY(selectedIndex()) - 50}`"
      />
      <rect :x="markerX(selectedIndex()) + 76" :y="markerY(selectedIndex()) - 82" width="178" height="52" />
      <text :x="markerX(selectedIndex()) + 88" :y="markerY(selectedIndex()) - 62">
        {{ selectedIncident.report_id }} / {{ fmtPct(selectedIncident.scenario_risk) }}
      </text>
      <text :x="markerX(selectedIndex()) + 88" :y="markerY(selectedIndex()) - 43" class="callout-sub">
        {{ selectedIncident.PHASE_OF_FLIGHT }} / {{ selectedIncident.SIZE_CLEAN }}
      </text>
    </g>

    <g class="surface-legend">
      <rect x="104" y="424" width="16" height="8" class="legend-green" />
      <text x="128" y="432">wildlife zone</text>
      <path d="M254 428 L286 428" class="legend-line" />
      <text x="296" y="432">approach corridor</text>
      <circle cx="462" cy="428" r="6" fill="#ff5c5c" />
      <text x="478" y="432">reported incidents</text>
    </g>
    <text x="106" y="456" class="layout-footer">Historical reported incident surface layer / scenario review / not live operations</text>
  </svg>
</template>
