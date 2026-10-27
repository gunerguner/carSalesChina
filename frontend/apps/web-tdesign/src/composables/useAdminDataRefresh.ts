import type {
  RefreshAllResult,
  RefreshProgressEvent,
  RefreshStreamError,
} from '#/api/admin';
import type {
  PhaseKey,
  RefreshProgressState,
} from '#/composables/useAdminDataRefresh.types';

import { ref } from 'vue';

import { refreshAllDataStream } from '#/api/admin';
import {
  applyProgressEvent,
  applyStreamDone,
  applyStreamError,
  createInitialProgressState,
  PHASE_ORDER,
} from '#/composables/useAdminDataRefresh.types';
import { $t } from '#/locales';
import { emitDataRefresh } from '#/utils/data-refresh';

const refreshing = ref(false);
const progressVisible = ref(false);
const progressState = ref<RefreshProgressState>(createInitialProgressState());

let abortController: AbortController | null = null;

export type RefreshStartResult =
  | { accepted: false; message: string }
  | { accepted: true };

function errorStatus(error: unknown): number | undefined {
  if (typeof error === 'object' && error !== null && 'status' in error) {
    const status = (error as { status: unknown }).status;
    return typeof status === 'number' ? status : undefined;
  }
  return undefined;
}

function isAuthRejection(status: number | undefined): boolean {
  return status === 401 || status === 429 || status === 503;
}

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

  function refreshAdminData(password: string): Promise<RefreshStartResult> {
    if (refreshing.value) {
      return Promise.resolve({ accepted: false, message: '' });
    }

    return new Promise((resolve) => {
      let accepted = false;
      const accept = () => {
        if (accepted) return;
        accepted = true;
        progressVisible.value = true;
        progressState.value.overallStatus = 'running';
        resolve({ accepted: true });
      };

      abortController?.abort();
      resetProgressState();
      refreshing.value = true;

      abortController = new AbortController();
      refreshAllDataStream(
        {
          onDone: (result: RefreshAllResult) => {
            accept();
            progressState.value = applyStreamDone(progressState.value, result);
            refreshing.value = false;
            abortController = null;
          },
          onError: (error: RefreshStreamError) => {
            accept();
            progressState.value = applyStreamError(progressState.value, error);
            refreshing.value = false;
            abortController = null;
          },
          onProgress: (event: RefreshProgressEvent) => {
            accept();
            progressState.value = applyProgressEvent(
              progressState.value,
              event,
            );
          },
        },
        password,
        abortController.signal,
      ).catch((error: unknown) => {
        if (abortController?.signal.aborted) return;
        const message = error instanceof Error ? error.message : '网络请求失败';
        if (!accepted && isAuthRejection(errorStatus(error))) {
          refreshing.value = false;
          progressVisible.value = false;
          abortController = null;
          resetProgressState();
          resolve({ accepted: false, message });
          return;
        }
        accept();
        progressState.value = applyStreamError(progressState.value, {
          message,
        });
        refreshing.value = false;
        abortController = null;
      });
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
