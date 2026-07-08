<script setup lang="ts">
import { computed } from "vue";
import { riskLevel } from "../utils/format";

const props = defineProps<{ rate: number }>();
const level = computed(() => riskLevel(props.rate));
</script>

<template>
  <span class="risk-pill" :class="level.toLowerCase()">{{ level }}</span>
</template>
