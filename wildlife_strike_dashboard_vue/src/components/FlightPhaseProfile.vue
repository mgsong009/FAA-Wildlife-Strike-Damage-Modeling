<script setup lang="ts">
import type { RiskRow } from "../types";
import { fmtPct, riskColor } from "../utils/format";

defineProps<{ rows: RiskRow[]; selected?: string }>();

const points = [
  { x: 120, y: 256 },
  { x: 270, y: 212 },
  { x: 438, y: 108 },
  { x: 616, y: 124 },
  { x: 780, y: 205 },
  { x: 912, y: 258 }
];
</script>

<template>
  <svg class="phase-profile" viewBox="0 0 1000 340" role="img" aria-label="Flight phase historical risk profile">
    <text x="62" y="310" class="phase-axis-label">Departure surface</text>
    <text x="752" y="310" class="phase-axis-label">Arrival surface</text>
    <path class="profile-runway" d="M52 276 H300" />
    <path class="profile-path" d="M64 260 C170 240 250 212 328 190 C454 154 482 66 628 116 C730 151 802 218 940 255" />
    <path class="profile-runway" d="M744 276 H960" />
    <path class="profile-altitude-band" d="M80 250 C220 220 300 200 390 150 C500 88 570 94 666 132 C760 170 842 226 922 254" />
    <text x="468" y="64" class="phase-axis-label">Historical phase damage profile</text>
    <g v-for="(row, index) in rows.slice(0, 6)" :key="row.category">
      <circle
        :cx="points[index].x"
        :cy="points[index].y"
        :r="selected === row.category ? 28 : 22"
        :fill="riskColor(row.damage_rate)"
        :class="{ selected: selected === row.category }"
      />
      <text :x="points[index].x" :y="points[index].y - 36" text-anchor="middle">{{ row.category }}</text>
      <text :x="points[index].x" :y="points[index].y + 5" text-anchor="middle" class="inside">{{ fmtPct(row.damage_rate) }}</text>
    </g>
  </svg>
</template>
