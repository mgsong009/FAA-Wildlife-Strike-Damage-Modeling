<script setup lang="ts">
import type { FilterState, StrikeRecord } from '../types';
import { filterColumn, filterLabel, filterOptions } from '../utils/filters';

const props = defineProps<{
  rows: StrikeRecord[];
  filters: FilterState;
  minCount: number;
}>();

const emit = defineEmits<{
  filtersChanged: [filters: FilterState];
  minCountChanged: [minCount: number];
}>();

const keys: (keyof FilterState)[] = ['month', 'phase', 'altitude', 'distance', 'size', 'species', 'numStruck', 'acClass', 'acMass', 'faaRegion', 'state'];

function updateFilter(key: keyof FilterState, event: Event) {
  const selected = Array.from((event.target as HTMLSelectElement).selectedOptions).map((option) => option.value);
  emit('filtersChanged', { ...props.filters, [key]: selected });
}
</script>

<template>
  <aside class="filter-panel">
    <div>
      <p class="eyebrow">Global Filters</p>
      <h2>분석 조건</h2>
    </div>
    <label>
      최소 표본 수
      <select :value="minCount" @change="emit('minCountChanged', Number(($event.target as HTMLSelectElement).value))">
        <option :value="30">30</option>
        <option :value="50">50</option>
        <option :value="100">100</option>
        <option :value="200">200</option>
      </select>
    </label>
    <label v-for="key in keys" :key="key">
      {{ filterLabel(key) }}
      <select multiple :value="filters[key]" @change="updateFilter(key, $event)">
        <option v-for="option in filterOptions(rows, filterColumn(key))" :key="option" :value="option">
          {{ option }}
        </option>
      </select>
    </label>
  </aside>
</template>
