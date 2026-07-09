import { ref } from 'vue';

import {
  refreshAllDataStream,
  type RefreshAllResult,
  type RefreshProgressEvent,
  type RefreshStreamError,
} from '#/api/admin';
import {
  applyProgressEvent,
  applyStreamDone,
  applyStreamError,
  createInitialProgressState,
  PHASE_ORDER,
  type PhaseKey,
  type RefreshProgressState,
} from '#/composables/useAdminDataRefresh.types';
import { $t } from '#/locales';
import { emitDataRefresh } from '#/utils/data-refresh';

const refreshing = ref(false);
const progressVisible = ref(false);
const progressState = ref<RefreshProgressState>(createInitialProgressState());

let abortController: AbortController | null = null;

function getPhaseLabels(): Record<PhaseKey, string> {
  return {
    brand_meta: $t('pages.admin.progress.phase.brandMeta'),
    origin: $t('pages.admin.progress.phase.origin'),
    sales: $t('pages.admin.progress.phase.sales'),
  };
}

function initProgressState(): RefreshProgressState {
  const labels = getPhaseLabels();
  const state = createInitialProgressState();
  PHASE_ORDER.forEach((key) => {
    state.phases[key].label = labels[key];
  });
  return state;
}

export function useAdminDataRefresh() {
  function resetProgressState() {
    progressState.value = initProgressState();
  }

  function refreshAdminData() {
    if (refreshing.value) return;

    abortController?.abort();
    resetProgressState();
    refreshing.value = true;
    progressVisible.value = true;
    progressState.value.overallStatus = 'running';

    abortController = refreshAllDataStream({
      onDone: (result: RefreshAllResult) => {
        progressState.value = applyStreamDone(progressState.value, result);
        refreshing.value = false;
        abortController = null;
      },
      onError: (error: RefreshStreamError) => {
        progressState.value = applyStreamError(progressState.value, error);
        refreshing.value = false;
        abortController = null;
      },
      onProgress: (event: RefreshProgressEvent) => {
        progressState.value = applyProgressEvent(progressState.value, event);
      },
    });
  }

  function closeProgressModal() {
    if (refreshing.value) return;
    progressVisible.value = false;
    if (progressState.value.overallStatus === 'done') {
      emitDataRefresh();
    }
    resetProgressState();
  }

  return {
    closeProgressModal,
    progressState,
    progressVisible,
    refreshAdminData,
    refreshing,
  };
}
