<script setup lang="ts">
import { InfoCircleIcon } from 'tdesign-icons-vue-next';
import { Tooltip } from 'tdesign-vue-next';

defineProps<{
  content: string;
}>();
</script>

<template>
  <Tooltip
    :content="content"
    placement="top"
    :max-width="320"
    :overlay-inner-style="{ whiteSpace: 'pre-line' }"
  >
    <InfoCircleIcon class="metric-tip-icon" />
  </Tooltip>
</template>

<style scoped>
.metric-tip-icon {
  font-size: 14px;
  vertical-align: middle;
  color: var(--tone-muted);
  cursor: help;
}
</style>
