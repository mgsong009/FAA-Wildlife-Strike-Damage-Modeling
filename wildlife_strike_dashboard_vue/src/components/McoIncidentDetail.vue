<script setup lang="ts">
import type { IncidentRow } from "../types";

defineProps<{ incident: IncidentRow | undefined }>();

function scoreDots(score: number | undefined): string {
  const rounded = Math.max(1, Math.min(5, Math.round(score ?? 1)));
  return "#".repeat(rounded) + "-".repeat(5 - rounded);
}
</script>

<template>
  <aside class="mco-console-card mco-incident-detail">
    <div class="mco-detail-header">
      <div>
        <p>Incident Detail</p>
        <h2><i :class="`status-${(incident?.status ?? 'NONE').toLowerCase()}`"></i>{{ incident?.report_id }}</h2>
      </div>
      <span>NEW</span>
    </div>

    <div class="mco-detail-rows">
      <div><span>PF</span><small>Phase of Flight</small><strong>{{ incident?.PHASE_OF_FLIGHT }}</strong></div>
      <div><span>ALT</span><small>Altitude</small><strong>{{ incident?.ALTITUDE_GROUP }}</strong></div>
      <div><span>LOC</span><small>Location</small><strong>{{ incident?.surface_location }}</strong></div>
      <div><span>SP</span><small>Species</small><strong>{{ incident?.SPECIES }}</strong></div>
      <div><span>SZ</span><small>Size</small><strong>{{ incident?.SIZE_CLEAN }}</strong></div>
      <div><span>IP</span><small>Impact Position</small><strong>{{ incident?.impact_position }}</strong></div>
      <div><span>DMG</span><small>Damage</small><strong><b :class="`status-badge status-${(incident?.status ?? 'NONE').toLowerCase()}`">{{ incident?.status }}</b></strong></div>
      <div><span>REV</span><small>Review Score</small><strong class="mco-stars">{{ scoreDots(incident?.review_score_5) }} <em>{{ incident?.review_score_5 ?? 1 }} / 5.0</em></strong></div>
      <div><span>NT</span><small>Notes</small><strong>{{ incident?.notes }}</strong></div>
    </div>

    <button type="button" class="mco-report-button">View Full Report</button>
    <p class="mco-detail-disclaimer">Historical FAA wildlife strike reports. Not real-time airport operations.</p>
  </aside>
</template>
