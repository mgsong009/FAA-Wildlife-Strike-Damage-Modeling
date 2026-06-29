<script setup lang="ts">
defineProps<{
  title: string;
  subtitle: string;
  mode: 'collision' | 'flight' | 'altitude' | 'wildlife' | 'model';
  stat?: string;
}>();
</script>

<template>
  <section class="explainer">
    <div class="explainer-visual" :class="mode">
      <template v-if="mode === 'collision'">
        <div class="aircraft">AIRCRAFT</div>
        <div class="impact-line"></div>
        <div class="bird">WILDLIFE</div>
        <div class="split">
          <span>No Damage</span>
          <span>Damage</span>
        </div>
      </template>
      <template v-else-if="mode === 'flight'">
        <div class="runway"></div>
        <div class="route">
          <span>Taxi</span><span>Take-off</span><span>Climb</span><span>Approach</span><span>Landing</span>
        </div>
      </template>
      <template v-else-if="mode === 'altitude'">
        <div class="alt-axis"><span>10,000 ft+</span><span>1,500 ft</span><span>0 ft</span></div>
        <div class="aircraft-icon">AIR</div>
      </template>
      <template v-else-if="mode === 'wildlife'">
        <div class="size-row"><span class="small-dot"></span><span class="mid-dot"></span><span class="large-dot"></span></div>
      </template>
      <template v-else>
        <div class="matrix-icon"><span>TN</span><span>FP</span><span class="warn">FN</span><span>TP</span></div>
      </template>
    </div>
    <div>
      <h3>{{ title }}</h3>
      <p>{{ subtitle }}</p>
      <strong v-if="stat">{{ stat }}</strong>
    </div>
  </section>
</template>
