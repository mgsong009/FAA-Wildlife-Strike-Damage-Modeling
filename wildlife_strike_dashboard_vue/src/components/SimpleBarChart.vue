<script setup lang="ts">
import { computed } from "vue";
import { fmtCount, fmtPct, riskColor } from "../utils/format";

const props = defineProps<{
  rows: Array<{ label: string; value: number; detail?: number; count?: number }>;
  valueLabel?: "percent" | "number";
  limit?: number;
}>();

const visibleRows = computed(() => props.rows.slice(0, props.limit ?? props.rows.length));
const maxValue = computed(() => Math.max(...visibleRows.value.map((row) => row.value), 0.001));
</script>

<template>
  <div class="bar-chart">
    <div v-for="row in visibleRows" :key="row.label" class="bar-row">
      <div class="bar-label">
        <span>{{ row.label }}</span>
        <small v-if="row.count !== undefined">{{ fmtCount(row.count) }} reports</small>
      </div>
      <div class="bar-track">
        <div
          class="bar-fill"
          :style="{ width: `${Math.max((row.value / maxValue) * 100, 2)}%`, background: riskColor(row.value) }"
        />
      </div>
      <strong>{{ valueLabel === "number" ? row.value.toFixed(2) : fmtPct(row.value) }}</strong>
    </div>
  </div>
</template>
