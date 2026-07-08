<script setup lang="ts">
import { computed } from "vue";
import { fmtPct, riskColor, riskLevel } from "../utils/format";

const props = defineProps<{
  value: number;
  label: string;
}>();

const level = computed(() => riskLevel(props.value));
</script>

<template>
  <div class="risk-gauge">
    <div class="gauge-arc" :style="{ '--gauge': `${Math.min(value, 0.45) / 0.45 * 180}deg`, '--gauge-color': riskColor(value) }">
      <strong>{{ fmtPct(value, 1) }}</strong>
      <span>{{ level }}</span>
    </div>
    <p>{{ label }}</p>
  </div>
</template>
