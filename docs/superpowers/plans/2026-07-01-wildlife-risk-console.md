# Wildlife Risk Console Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a new Vue dashboard that presents FAA wildlife strike damage risk results as an aviation-style analysis console with one operator map demonstration tab.

**Architecture:** Rebuild `wildlife_strike_dashboard_vue` as a compact Vue 3 + TypeScript app. Static CSV artifacts are served from `public/data`, parsed in browser, and transformed by small utility modules. Visuals use SVG/CSS instead of a heavy charting dependency so the dashboard remains easy to run and modify.

**Tech Stack:** Vue 3, TypeScript, Vite, CSS, static CSV generated from existing FAA model outputs.

---

### Task 1: Data Artifacts

**Files:**
- Create/update: `wildlife_strike_dashboard_vue/public/data/*.csv`

- [ ] Copy existing model output CSVs needed by the dashboard.
- [ ] Generate operator-level map data from `FAA_0619_preprocessed_dataset_for_team.xlsx`.
- [ ] Generate summary CSVs for total dataset and Southwest operator phase risk.

### Task 2: App Scaffold

**Files:**
- Create: `wildlife_strike_dashboard_vue/package.json`
- Create: `wildlife_strike_dashboard_vue/index.html`
- Create: `wildlife_strike_dashboard_vue/tsconfig.json`
- Create: `wildlife_strike_dashboard_vue/vite.config.ts`
- Create: `wildlife_strike_dashboard_vue/src/main.ts`
- Create: `wildlife_strike_dashboard_vue/src/App.vue`
- Create: `wildlife_strike_dashboard_vue/src/styles.css`

- [ ] Create a Vue/Vite app with tab navigation.
- [ ] Use the page order: Overview, Flight Phase Risk, Risk Factors, Operator Scenario Map, Model Performance, Limitations.
- [ ] Keep labels defensive: reported incidents, post-strike review, screening support.

### Task 3: Shared Utilities and Components

**Files:**
- Create: `wildlife_strike_dashboard_vue/src/types.ts`
- Create: `wildlife_strike_dashboard_vue/src/utils/csv.ts`
- Create: `wildlife_strike_dashboard_vue/src/utils/format.ts`
- Create: `wildlife_strike_dashboard_vue/src/components/KpiCard.vue`
- Create: `wildlife_strike_dashboard_vue/src/components/SimpleBarChart.vue`
- Create: `wildlife_strike_dashboard_vue/src/components/RiskPill.vue`

- [ ] Add typed CSV parsing and numeric coercion.
- [ ] Add shared formatting helpers for percentages and counts.
- [ ] Add reusable KPI, risk badge, and SVG bar chart components.

### Task 4: Dashboard Pages

**Files:**
- Modify: `wildlife_strike_dashboard_vue/src/App.vue`

- [ ] Overview: dataset scale, damage rate, screening flow, top model drivers.
- [ ] Flight Phase Risk: aircraft profile diagram and phase risk bars.
- [ ] Risk Factors: size, altitude, number struck, species, and distance risk sections.
- [ ] Operator Scenario Map: Southwest as highest reported operator, airport incident map, airport detail panel, phase strip.
- [ ] Model Performance: final metrics, confusion matrix, model comparison, feature importance.
- [ ] Limitations: allowed claims, avoided claims, operator map caveats.

### Task 5: Verification

**Files:**
- Run: `npm install`
- Run: `npm run build`
- Run: `npm run dev`

- [ ] Install dependencies if needed.
- [ ] Build the app.
- [ ] Start the dev server and report the local URL.
- [ ] If browser tools are available, visually inspect the first screen and operator map.
