<script setup lang="ts">
import MetricTooltip from './MetricTooltip.vue';

defineProps<{
  title: string;
  tooltip?: string;
}>();
</script>

<template>
  <div class="section-card">
    <div class="section-card__header">
      <span class="section-card__title">{{ title }}</span>
      <MetricTooltip v-if="tooltip" :content="tooltip" />
    </div>
    <div class="section-card__body">
      <slot></slot>
    </div>
  </div>
</template>

<style scoped>
.section-card {
  margin-bottom: 1.25rem;
  background: hsl(var(--card));
  border: 1px solid hsl(var(--border));
  border-radius: var(--radius);
}

.section-card__header {
  display: flex;
  align-items: center;
  gap: 4px;
  padding: 0.75rem 1.25rem;
  border-bottom: 1px solid hsl(var(--border));
}

.section-card__title {
  font-size: 0.875rem;
  font-weight: 500;
  color: hsl(var(--muted-foreground));
}

.section-card__body {
  padding: 1rem 1.25rem;
}
</style>
