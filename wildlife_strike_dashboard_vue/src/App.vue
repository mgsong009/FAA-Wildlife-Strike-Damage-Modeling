<script setup lang="ts">
import { computed, onMounted, reactive, ref } from 'vue';
import FilterPanel from './components/FilterPanel.vue';
import KpiCard from './components/KpiCard.vue';
import PlotlyChart from './components/PlotlyChart.vue';
import VisualExplainer from './components/VisualExplainer.vue';
import type { FilterState, MetricRow, PredictionRow, RiskStat, StrikeRecord } from './types';
import {
  confusionMatrix,
  damageDonut,
  featureImportance,
  frequencySeverityMatrix,
  modelMetricComparison,
  monthlyTrend,
  phaseAltitudeHeatmap,
  riskBar
} from './utils/charts';
import { compactNumber, formatPercent, loadDashboardData, type NormalizedMetricRow } from './utils/data';
import { applyFilters, createEmptyFilters } from './utils/filters';
import { calculateDamageRate, calculateOverallDamageRate } from './utils/risk';

type PageKey = 'overview' | 'flight' | 'wildlife' | 'matrix' | 'model' | 'insight';

interface DashboardData {
  strikes: StrikeRecord[];
  metrics: NormalizedMetricRow[];
  finalMetrics: NormalizedMetricRow[];
  predictions: PredictionRow[];
  featureImportance: Record<string, string | number>[];
}

const pages: { key: PageKey; label: string }[] = [
  { key: 'overview', label: 'Risk Overview' },
  { key: 'flight', label: 'Flight Condition' },
  { key: 'wildlife', label: 'Wildlife Impact' },
  { key: 'matrix', label: 'Frequency-Severity' },
  { key: 'model', label: 'Model Performance' },
  { key: 'insight', label: 'Final Insight' }
];

const data = ref<DashboardData | null>(null);
const loadError = ref('');
const activePage = ref<PageKey>('overview');
const minCount = ref(50);
const filters = reactive<FilterState>(createEmptyFilters());
const matrixGroup = ref<keyof StrikeRecord>('PHASE_OF_FLIGHT');
const selectedModel = ref('Decision Tree');

onMounted(async () => {
  try {
    data.value = await loadDashboardData();
  } catch (error) {
    loadError.value = error instanceof Error ? error.message : '데이터를 불러오지 못했습니다.';
  }
});

const filteredRows = computed(() => (data.value ? applyFilters(data.value.strikes, filters) : []));
const totalCases = computed(() => filteredRows.value.length);
const damagedCases = computed(() => filteredRows.value.reduce((sum, row) => sum + Number(row.Damage_Binary || 0), 0));
const damageRate = computed(() => calculateOverallDamageRate(filteredRows.value));

const phaseStats = computed(() => calculateDamageRate(filteredRows.value, 'PHASE_OF_FLIGHT', minCount.value));
const altitudeStats = computed(() => calculateDamageRate(filteredRows.value, 'ALTITUDE_GROUP', minCount.value));
const sizeStats = computed(() => calculateDamageRate(filteredRows.value, 'SIZE_CLEAN', minCount.value));
const numStruckStats = computed(() => calculateDamageRate(filteredRows.value, 'NUM_STRUCK', minCount.value));
const speciesStats = computed(() => calculateDamageRate(filteredRows.value, 'SPECIES', minCount.value));
const matrixStats = computed(() => calculateDamageRate(filteredRows.value, matrixGroup.value, minCount.value));

const modelRows = computed<MetricRow[]>(() => data.value?.metrics ?? []);
const finalModelMetric = computed(() => data.value?.finalMetrics[0]);
const modelNames = computed(() => Array.from(new Set(data.value?.predictions.map((row) => row.model_name) ?? [])));

const topPriority = computed(() =>
  matrixStats.value
    .filter((row) => row.minCountPass && row.damageRate >= row.overallDamageRate)
    .slice(0, 3)
    .map((row) => row.category)
    .join(', ')
);

function replaceFilters(nextFilters: FilterState) {
  Object.assign(filters, nextFilters);
}

function firstStatLabel(stats: RiskStat[], fallback: string): string {
  const first = stats.find((row) => row.minCountPass) ?? stats[0];
  if (!first) return fallback;
  return `${first.category}: ${formatPercent(first.damageRate)} / avg diff ${(first.damageRate - first.overallDamageRate).toFixed(1)}%p`;
}
</script>

<template>
  <div v-if="loadError" class="error">{{ loadError }}</div>
  <div v-else-if="!data" class="loading">Dashboard data loading...</div>
  <div v-else class="app-shell">
    <FilterPanel
      :rows="data.strikes"
      :filters="filters"
      :min-count="minCount"
      @filters-changed="replaceFilters"
      @min-count-changed="minCount = $event"
    />

    <main class="main">
      <header class="page-title">
        <div>
          <p class="eyebrow">FAA Wildlife Strike Damage Risk</p>
          <h1>시연형 손상 위험 탐색 대시보드</h1>
          <p>
            충돌 발생 자체가 아니라, 이미 발생한 wildlife strike 이후 항공기 손상 가능성이 높은 조건을 탐색합니다.
            핵심 메시지는 충돌 빈도와 손상 위험이 다를 수 있다는 점입니다.
          </p>
        </div>
      </header>

      <nav class="tabs" aria-label="Dashboard sections">
        <button
          v-for="page in pages"
          :key="page.key"
          :class="{ active: activePage === page.key }"
          type="button"
          @click="activePage = page.key"
        >
          {{ page.label }}
        </button>
      </nav>

      <section class="kpi-grid">
        <KpiCard label="Total Cases" :value="compactNumber(totalCases)" note="현재 필터 기준" />
        <KpiCard label="Damaged Cases" :value="compactNumber(damagedCases)" tone="red" />
        <KpiCard label="Damage Rate" :value="formatPercent(damageRate, 2)" tone="orange" />
        <KpiCard label="Target" value="Damage_Binary" note="0 = no damage, 1 = damage" tone="mint" />
      </section>

      <section v-if="activePage === 'overview'" class="grid">
        <div class="chart-grid">
          <div class="panel"><PlotlyChart :spec="damageDonut(filteredRows)" /></div>
          <div class="panel"><PlotlyChart :spec="monthlyTrend(filteredRows)" /></div>
        </div>
        <VisualExplainer
          mode="collision"
          title="충돌 이후 손상 여부 분석"
          subtitle="이 화면은 실시간 위험 예측이 아니라, 충돌 사고 데이터에서 손상 여부를 분석한 시연형 대시보드입니다."
          :stat="`현재 손상률 ${formatPercent(damageRate, 2)}`"
        />
      </section>

      <section v-else-if="activePage === 'flight'" class="grid">
        <div class="chart-grid">
          <div class="panel"><PlotlyChart :spec="riskBar(phaseStats, 'Damage Rate by Flight Phase')" /></div>
          <div class="panel"><PlotlyChart :spec="riskBar(altitudeStats, 'Damage Rate by Altitude')" /></div>
          <div class="panel"><PlotlyChart :spec="phaseAltitudeHeatmap(filteredRows, minCount)" /></div>
        </div>
        <div class="chart-grid">
          <VisualExplainer
            mode="flight"
            title="비행단계 해석"
            subtitle="이륙, 상승, 접근, 착륙 같은 단계별 손상률을 전체 평균과 비교해 봅니다."
            :stat="firstStatLabel(phaseStats, '선택 가능한 비행단계가 없습니다')"
          />
          <VisualExplainer
            mode="altitude"
            title="고도구간 해석"
            subtitle="고도 구간은 충돌 위치의 맥락을 설명하며, 특정 구간은 충돌 건수보다 손상률이 더 중요할 수 있습니다."
            :stat="firstStatLabel(altitudeStats, '선택 가능한 고도구간이 없습니다')"
          />
        </div>
      </section>

      <section v-else-if="activePage === 'wildlife'" class="grid">
        <div class="chart-grid">
          <div class="panel"><PlotlyChart :spec="riskBar(sizeStats, 'Damage Rate by Wildlife Size', 8)" /></div>
          <div class="panel"><PlotlyChart :spec="riskBar(numStruckStats, 'Damage Rate by Number Struck', 10)" /></div>
          <div class="panel"><PlotlyChart :spec="riskBar(speciesStats, 'Species Risk Top 10', 10)" /></div>
        </div>
        <VisualExplainer
          mode="wildlife"
          title="동물 요인 해석"
          subtitle="동물 크기와 충돌 개체 수는 충돌 에너지와 손상 가능성의 직관적 설명 변수입니다."
          :stat="firstStatLabel(sizeStats, '선택 가능한 동물 크기가 없습니다')"
        />
      </section>

      <section v-else-if="activePage === 'matrix'">
        <div class="panel">
          <label>
            분석 단위
            <select v-model="matrixGroup">
              <option value="PHASE_OF_FLIGHT">PHASE_OF_FLIGHT</option>
              <option value="ALTITUDE_GROUP">ALTITUDE_GROUP</option>
              <option value="SIZE_CLEAN">SIZE_CLEAN</option>
              <option value="SPECIES">SPECIES</option>
              <option value="AC_MASS">AC_MASS</option>
              <option value="FAAREGION">FAAREGION</option>
            </select>
          </label>
          <PlotlyChart :spec="frequencySeverityMatrix(matrixStats)" />
          <p>
            현재 기준에서 우선 확인할 조건은
            <strong>{{ topPriority || '최소 표본 기준을 통과한 고위험 조건 없음' }}</strong>
            입니다. 충돌이 많이 발생하는 조건과 실제 손상률이 높은 조건은 다를 수 있습니다.
          </p>
        </div>
      </section>

      <section v-else-if="activePage === 'model'" class="grid">
        <div class="chart-grid">
          <div class="panel">
            <label>
              모델 선택
              <select v-model="selectedModel">
                <option v-for="model in modelNames" :key="model" :value="model">{{ model }}</option>
              </select>
            </label>
            <PlotlyChart :spec="modelMetricComparison(modelRows)" />
          </div>
          <div class="panel"><PlotlyChart :spec="confusionMatrix(data.predictions, selectedModel)" /></div>
          <div class="panel"><PlotlyChart :spec="featureImportance(data.featureImportance)" /></div>
        </div>
        <VisualExplainer
          mode="model"
          title="False Negative 중심 해석"
          subtitle="실제로는 손상이 있었지만 모델이 비손상으로 예측한 경우입니다. 항공안전 관점에서는 Accuracy보다 Recall과 F1-score를 함께 봐야 합니다."
          :stat="finalModelMetric ? `Final recall ${formatPercent(finalModelMetric.recall * 100, 1)} / F1 ${finalModelMetric.f1.toFixed(3)}` : ''"
        />
      </section>

      <section v-else class="insight-grid">
        <article class="insight-card">
          <p class="eyebrow">Insight 01</p>
          <h2>Frequency does not equal risk</h2>
          <p>충돌이 많이 발생하는 조건과 실제 항공기 손상률이 높은 조건은 다를 수 있습니다.</p>
        </article>
        <article class="insight-card">
          <p class="eyebrow">Insight 02</p>
          <h2>Risk comes from combinations</h2>
          <p>비행단계, 고도구간, 동물 크기, 충돌 개체 수의 조합이 손상 위험 해석에 중요합니다.</p>
        </article>
        <article class="insight-card">
          <p class="eyebrow">Insight 03</p>
          <h2>Screening, not final judgment</h2>
          <p>본 모델은 손상 여부를 확정하는 도구가 아니라, 손상 가능성이 높은 사고를 우선 선별하는 스크리닝 도구입니다.</p>
        </article>
      </section>
    </main>
  </div>
</template>
