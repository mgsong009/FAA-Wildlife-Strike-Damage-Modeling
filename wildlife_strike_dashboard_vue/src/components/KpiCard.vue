<script setup lang="ts">
defineProps<{
  label: string;
  value: string;
  note?: string;
  tone?: 'cyan' | 'mint' | 'orange' | 'red';
}>();
</script>

<template>
  <section class="kpi-card" :class="tone ?? 'cyan'">
    <span>{{ label }}</span>
    <strong>{{ value }}</strong>
    <small v-if="note">{{ note }}</small>
  </section>
</template>
