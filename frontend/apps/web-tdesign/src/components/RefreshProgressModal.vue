<script setup lang="ts">
import type {
  PhaseKey,
  PhaseStatus,
} from '#/composables/useAdminDataRefresh.types';

import { computed } from 'vue';

import { Button, Collapse, CollapsePanel, Dialog } from 'tdesign-vue-next';

import { useAdminDataRefresh } from '#/composables/useAdminDataRefresh';
import { PHASE_ORDER } from '#/composables/useAdminDataRefresh.types';
import { $t } from '#/locales';

const { closeProgressModal, progressState, progressVisible, refreshing } =
  useAdminDataRefresh();

const visible = computed(() => progressVisible.value);
const phaseOrder = PHASE_ORDER;

const canClose = computed(
  () =>
    !refreshing.value &&
    (progressState.value.overallStatus === 'done' ||
      progressState.value.overallStatus === 'error'),
);

const errorDetails = computed(() => {
  const lines: string[] = [];
  phaseOrder.forEach((key) => {
    const item = progressState.value.phases[key];
    if (!item.source_errors) return;
    Object.entries(item.source_errors).forEach(([source, message]) => {
      if (message) {
        lines.push(`${item.label}(${source}): ${message}`);
      }
    });
  });
  return lines;
});

function phaseIcon(key: PhaseKey): string {
  const { status } = progressState.value.phases[key];
  if (status === 'done') return '✓';
  if (status === 'running') return '⟳';
  if (status === 'failed') return '✗';
  return '·';
}

function phaseMetric(key: PhaseKey): string {
  const item = progressState.value.phases[key];
  if (item.status === 'pending') return '—';
  if (key === 'sales' && item.total > 0 && item.status === 'running') {
    return `${item.current}/${item.total.toLocaleString()}`;
  }
  if (item.imported > 0 || item.status === 'done' || item.status === 'failed') {
    return `${item.imported.toLocaleString()} ${$t('pages.admin.progress.rows')}`;
  }
  return item.detail || '—';
}

function formatElapsed(elapsed?: number): string {
  if (elapsed === undefined || elapsed === null) return '—';
  return `${elapsed.toFixed(1)}s`;
}

function phaseStatusText(key: PhaseKey): string {
  const { status } = progressState.value.phases[key];
  const map: Record<PhaseStatus, string> = {
    pending: $t('pages.admin.progress.status.pending'),
    running: $t('pages.admin.progress.status.running'),
    done: $t('pages.admin.progress.status.done'),
    failed: $t('pages.admin.progress.status.failed'),
  };
  return map[status];
}

function handleClose() {
  closeProgressModal();
}
</script>

<template>
  <Dialog
    :visible="visible"
    :header="$t('pages.admin.progress.title')"
    :close-on-overlay-click="false"
    :close-btn="false"
    :footer="false"
    width="640px"
    destroy-on-close
  >
    <div class="progress-summary">
      <div class="progress-summary__label">
        {{ $t('pages.admin.progress.overall') }}
        <span class="progress-summary__count">
          {{ progressState.completedCount }}/{{ progressState.totalPhases }}
        </span>
      </div>
    </div>

    <div class="phase-list">
      <div
        v-for="phaseKey in phaseOrder"
        :key="phaseKey"
        class="phase-row"
        :class="`phase-row--${progressState.phases[phaseKey].status}`"
      >
        <span class="phase-row__icon">{{ phaseIcon(phaseKey) }}</span>
        <span class="phase-row__name">
          {{ progressState.phases[phaseKey].label }}
        </span>
        <span class="phase-row__metric">
          {{ phaseMetric(phaseKey) }}
        </span>
        <span class="phase-row__elapsed">
          {{ formatElapsed(progressState.phases[phaseKey].elapsed) }}
        </span>
        <span class="phase-row__status">
          {{ phaseStatusText(phaseKey) }}
        </span>
      </div>
    </div>

    <Collapse
      v-if="errorDetails.length > 0"
      default-expand-all
      class="error-collapse"
    >
      <CollapsePanel
        :header="$t('pages.admin.progress.errorDetails')"
        value="errors"
      >
        <pre class="error-details">{{ errorDetails.join('\n') }}</pre>
      </CollapsePanel>
    </Collapse>

    <p v-if="progressState.errorMessage" class="error-message">
      {{ progressState.errorMessage }}
    </p>

    <div v-if="canClose" class="modal-footer">
      <Button theme="primary" @click="handleClose">
        {{ $t('pages.admin.progress.close') }}
      </Button>
    </div>
  </Dialog>
</template>

<style scoped>
.progress-summary {
  margin-bottom: 20px;
}

.progress-summary__label {
  display: flex;
  justify-content: space-between;
  font-size: 14px;
  color: var(--td-text-color-secondary);
}

.progress-summary__count {
  color: var(--td-text-color-placeholder);
}

.phase-list {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.phase-row {
  display: grid;
  grid-template-columns: 24px 1fr 120px 56px 72px;
  gap: 8px;
  align-items: center;
  padding: 8px 10px;
  font-size: 14px;
  background: var(--td-bg-color-secondarycontainer);
  border-radius: 6px;
}

.phase-row--running,
.phase-row--done {
  background: var(--td-brand-color-light);
}

.phase-row--failed {
  background: var(--td-error-color-1);
}

.phase-row__icon {
  font-weight: 600;
  text-align: center;
}

.phase-row__name {
  color: var(--td-text-color-primary);
}

.phase-row__metric,
.phase-row__elapsed,
.phase-row__status {
  color: var(--td-text-color-placeholder);
  text-align: right;
  white-space: nowrap;
}

.error-collapse {
  margin-top: 16px;
}

.error-details {
  margin: 0;
  font-size: 12px;
  color: var(--td-text-color-secondary);
  overflow-wrap: anywhere;
  white-space: pre-wrap;
}

.error-message {
  margin-top: 12px;
  font-size: 14px;
  color: var(--td-error-color);
}

.modal-footer {
  display: flex;
  justify-content: flex-end;
  margin-top: 20px;
}
</style>
