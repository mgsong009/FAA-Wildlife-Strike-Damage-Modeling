<script setup lang="ts">
defineProps<{
  label: string;
  value: string;
  detail?: string;
  tone?: "neutral" | "green" | "amber" | "red" | "blue";
}>();
</script>

<template>
  <article class="kpi-card" :class="tone ?? 'neutral'">
    <span>{{ label }}</span>
    <strong>{{ value }}</strong>
    <small v-if="detail">{{ detail }}</small>
  </article>
</template>
