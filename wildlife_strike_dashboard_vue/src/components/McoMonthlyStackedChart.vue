<script setup lang="ts">
import type { McoMonthlyStatusRow } from "../types";
import { fmtCount } from "../utils/format";

const props = defineProps<{ rows: McoMonthlyStatusRow[] }>();
const maxTotal = Math.max(...props.rows.map((row) => row.total_count), 1);
</script>

<template>
  <article class="mco-console-card mco-monthly-chart">
    <div class="mco-card-title">
      <h2>Incidents Over Time <span>(Monthly)</span></h2>
      <div class="mco-chart-legend">
        <i class="damaged"></i> Damaged
        <i class="possible"></i> Possible
        <i class="none"></i> None
      </div>
    </div>
    <div class="mco-stacked-bars">
      <div
        v-for="row in rows"
        :key="row.INCIDENT_MONTH"
        class="mco-stacked-month"
        :class="{ peak: row.INCIDENT_MONTH >= 8 && row.INCIDENT_MONTH <= 10 }"
      >
        <div class="mco-stack" :style="{ height: `${Math.max(28, (row.total_count / maxTotal) * 104)}px` }">
          <b class="damaged" :style="{ flexGrow: row.damaged_count }"></b>
          <b class="possible" :style="{ flexGrow: row.possible_count }"></b>
          <b class="none" :style="{ flexGrow: row.none_count }"></b>
        </div>
        <strong>{{ fmtCount(row.total_count) }}</strong>
        <span>{{ row.INCIDENT_MONTH }}</span>
      </div>
    </div>
  </article>
</template>
