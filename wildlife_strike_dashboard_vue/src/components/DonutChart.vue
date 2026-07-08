<script setup lang="ts">
import { fmtPct } from "../utils/format";

defineProps<{
  value: number;
  label: string;
  tone?: "blue" | "amber" | "green" | "red";
}>();
</script>

<template>
  <div class="donut-unit">
    <div class="donut-chart" :class="tone ?? 'blue'" :style="{ '--angle': `${Math.min(value, 1) * 360}deg` }">
      <strong>{{ fmtPct(value, 0) }}</strong>
    </div>
    <span>{{ label }}</span>
  </div>
</template>
