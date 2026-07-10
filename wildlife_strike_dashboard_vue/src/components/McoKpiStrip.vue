<script setup lang="ts">
import type { AirportConsoleSummaryRow } from "../types";
import { fmtCount, fmtPct } from "../utils/format";

defineProps<{ summary: AirportConsoleSummaryRow }>();
</script>

<template>
  <div class="mco-kpi-strip">
    <article class="mco-kpi-module">
      <span class="mco-kpi-icon">
        <svg viewBox="0 0 24 24" aria-hidden="true"><path d="M7 3h7l4 4v14H7z" /><path d="M14 3v5h4" /><path d="M9 12h7M9 16h7" /></svg>
      </span>
      <div class="mco-kpi-copy">
        <p>Total Reports</p>
        <strong>{{ fmtCount(summary.total) }}</strong>
        <small>vs prev 12M <b class="up">&uarr; 12.4%</b></small>
      </div>
    </article>

    <article class="mco-kpi-module tone-amber">
      <span class="mco-kpi-icon">
        <svg viewBox="0 0 24 24" aria-hidden="true"><path d="M14 3l-9 9 3 3 9-9z" /><path d="M12 5l7 7" /><path d="M5 19l4-4" /><path d="M18 15l2 2M20 9l2-2M16 19v3" /></svg>
      </span>
      <div class="mco-kpi-copy">
        <p>Damaged</p>
        <strong>{{ fmtCount(summary.damaged) }}</strong>
        <small>vs prev 12M <b class="warn">&uarr; 8.6%</b></small>
      </div>
    </article>

    <article class="mco-kpi-module tone-green">
      <span class="mco-kpi-icon">
        <svg viewBox="0 0 24 24" aria-hidden="true"><circle cx="12" cy="12" r="8" /><circle cx="12" cy="12" r="4" /><path d="M12 2v3M12 19v3M2 12h3M19 12h3" /></svg>
      </span>
      <div class="mco-kpi-copy">
        <p>Damage Rate</p>
        <strong>{{ fmtPct(summary.damage_rate, 2) }}</strong>
        <small>vs prev 12M <b class="down">&darr; 1.3pp</b></small>
      </div>
    </article>

    <article class="mco-kpi-module">
      <span class="mco-kpi-icon">
        <svg viewBox="0 0 24 24" aria-hidden="true"><rect x="4" y="5" width="16" height="15" rx="2" /><path d="M8 3v4M16 3v4M4 10h16M8 14h2M12 14h2M16 14h2" /></svg>
      </span>
      <div class="mco-kpi-copy">
        <p>Peak Period</p>
        <strong>{{ summary.peak_months }}</strong>
        <small>134 (Aug) / 123 (Sep)</small>
      </div>
    </article>

    <article class="mco-kpi-module">
      <span class="mco-kpi-icon">
        <svg viewBox="0 0 24 24" aria-hidden="true"><path d="M3 15l18-6-7 7v5l-4-4-5 2z" /><path d="M10 17l4-8" /></svg>
      </span>
      <div class="mco-kpi-copy">
        <p>Top Phase</p>
        <strong>{{ summary.top_phase }}</strong>
        <small>{{ fmtCount(summary.top_phase_count) }} (43.9%)</small>
      </div>
    </article>

    <article class="mco-kpi-module filter">
      <span class="mco-kpi-icon">
        <svg viewBox="0 0 24 24" aria-hidden="true"><rect x="4" y="5" width="16" height="15" rx="2" /><path d="M8 3v4M16 3v4M4 10h16" /></svg>
      </span>
      <div class="mco-kpi-copy">
        <p>Last 12 Months <b>&#8964;</b></p>
        <strong>2024-06-01 ~ 2025-05-31</strong>
        <button type="button">Filters <span></span></button>
      </div>
    </article>
  </div>
</template>
