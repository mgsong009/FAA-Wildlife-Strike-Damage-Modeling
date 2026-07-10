<script setup lang="ts">
import type { McoSpeciesRow } from "../types";
import { fmtCount, fmtPct } from "../utils/format";

const props = defineProps<{ rows: McoSpeciesRow[] }>();

const total = props.rows.reduce((sum, row) => sum + Number(row.count), 0);
let offset = 25;
const segments = props.rows.map((row) => {
  const length = Math.max(0, Number(row.share) * 100);
  const segment = { ...row, dash: `${length} ${100 - length}`, offset };
  offset -= length;
  return segment;
});
</script>

<template>
  <article class="mco-console-card mco-species-card">
    <div class="mco-card-title">
      <h2>Top Species <span>(by reports)</span></h2>
    </div>
    <div class="mco-species-body">
      <svg viewBox="0 0 120 120" class="mco-donut">
        <circle cx="60" cy="60" r="38" class="base" />
        <circle
          v-for="row in segments"
          :key="row.species"
          cx="60"
          cy="60"
          r="38"
          :stroke="row.display_color"
          :stroke-dasharray="row.dash"
          :stroke-dashoffset="row.offset"
        />
      </svg>
      <div class="mco-species-list">
        <span v-for="row in rows" :key="row.species">
          <i :style="{ background: row.display_color }"></i>
          <b>{{ row.species }}</b>
          <em>{{ fmtCount(row.count) }} ({{ fmtPct(row.share) }})</em>
        </span>
        <strong>Total <b>{{ fmtCount(total) }}</b></strong>
      </div>
    </div>
  </article>
</template>
