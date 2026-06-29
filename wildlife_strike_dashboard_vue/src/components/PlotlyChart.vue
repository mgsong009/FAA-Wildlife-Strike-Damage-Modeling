<script setup lang="ts">
import Plotly from 'plotly.js-dist-min';
import { onBeforeUnmount, onMounted, ref, watch } from 'vue';
import type { PlotSpec } from '../utils/charts';

const props = defineProps<{
  spec: PlotSpec;
}>();

const chartEl = ref<HTMLDivElement | null>(null);

async function drawChart() {
  if (!chartEl.value) return;
  await Plotly.react(chartEl.value, props.spec.data, props.spec.layout, {
    responsive: true,
    displayModeBar: false
  });
}

onMounted(drawChart);
watch(() => props.spec, drawChart, { deep: true });

onBeforeUnmount(() => {
  if (chartEl.value) Plotly.purge(chartEl.value);
});
</script>

<template>
  <div ref="chartEl" class="plotly-chart"></div>
</template>
