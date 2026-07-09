import type {
  RefreshAllResult,
  RefreshProgressEvent,
  RefreshStreamError,
} from '#/api/admin';

export type PhaseKey = 'brand_meta' | 'origin' | 'sales';

export type PhaseStatus = 'done' | 'failed' | 'pending' | 'running';

export interface PhaseState {
  phase: PhaseKey;
  label: string;
  status: PhaseStatus;
  current: number;
  total: number;
  imported: number;
  detail?: string;
  elapsed?: number;
  source_errors?: null | Record<string, null | string>;
}

export type RefreshOverallStatus = 'done' | 'error' | 'idle' | 'running';

export interface RefreshProgressState {
  phases: Record<PhaseKey, PhaseState>;
  completedCount: number;
  totalPhases: number;
  overallStatus: RefreshOverallStatus;
  finalResult: null | RefreshAllResult;
  errorMessage: null | string;
  errorPhase: null | PhaseKey;
}

export const PHASE_ORDER: PhaseKey[] = ['brand_meta', 'sales', 'origin'];

export function createInitialProgressState(): RefreshProgressState {
  return {
    phases: {
      brand_meta: {
        phase: 'brand_meta',
        label: '',
        status: 'pending',
        current: 0,
        total: 1,
        imported: 0,
      },
      origin: {
        phase: 'origin',
        label: '',
        status: 'pending',
        current: 0,
        total: 1,
        imported: 0,
      },
      sales: {
        phase: 'sales',
        label: '',
        status: 'pending',
        current: 0,
        total: 0,
        imported: 0,
      },
    },
    completedCount: 0,
    totalPhases: PHASE_ORDER.length,
    overallStatus: 'idle',
    finalResult: null,
    errorMessage: null,
    errorPhase: null,
  };
}

function mapProgressStatus(
  status: RefreshProgressEvent['status'],
): PhaseStatus {
  if (status === 'running') return 'running';
  if (status === 'done') return 'done';
  if (status === 'failed') return 'failed';
  return 'pending';
}

export function applyProgressEvent(
  state: RefreshProgressState,
  event: RefreshProgressEvent,
): RefreshProgressState {
  const { phase } = event;
  const nextPhases = { ...state.phases };
  const prev = nextPhases[phase];
  const nextStatus = mapProgressStatus(event.status);

  nextPhases[phase] = {
    ...prev,
    phase,
    label: event.label || prev.label,
    status: nextStatus,
    current: event.current ?? prev.current,
    total: event.total ?? prev.total,
    imported: event.imported ?? prev.imported,
    detail: event.detail ?? prev.detail,
    elapsed: event.elapsed ?? prev.elapsed,
    source_errors: event.source_errors ?? prev.source_errors,
  };

  const completedCount = PHASE_ORDER.filter((key) => {
    const item = nextPhases[key];
    return item.status === 'done' || item.status === 'failed';
  }).length;

  return {
    ...state,
    phases: nextPhases,
    completedCount,
    overallStatus: 'running',
  };
}

export function applyStreamError(
  state: RefreshProgressState,
  error: RefreshStreamError,
): RefreshProgressState {
  const errorPhase = (error.phase as PhaseKey | undefined) ?? null;
  const nextPhases = { ...state.phases };
  if (errorPhase && nextPhases[errorPhase]) {
    nextPhases[errorPhase] = {
      ...nextPhases[errorPhase],
      status: 'failed',
    };
  }

  return {
    ...state,
    phases: nextPhases,
    overallStatus: 'error',
    errorMessage: error.message,
    errorPhase,
  };
}

export function applyStreamDone(
  state: RefreshProgressState,
  result: RefreshAllResult,
): RefreshProgressState {
  const nextPhases = { ...state.phases };
  PHASE_ORDER.forEach((key) => {
    const item = result[key];
    if (!item) return;
    nextPhases[key] = {
      ...nextPhases[key],
      status: item.status === 'failed' ? 'failed' : 'done',
      imported: item.imported,
      total: item.total,
      elapsed: item.elapsed,
      source_errors: item.source_errors,
    };
  });

  return {
    ...state,
    phases: nextPhases,
    completedCount: PHASE_ORDER.length,
    overallStatus: 'done',
    finalResult: result,
    errorMessage: null,
    errorPhase: null,
  };
}
