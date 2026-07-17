import { useAppConfig } from '@vben/hooks';

import { streamPost } from '#/utils/sse-stream';

export type RefreshStatus = 'failed' | 'partial_failure' | 'success';

export interface RefreshResultItem {
  imported: number;
  total: number;
  status: 'skipped' | RefreshStatus;
  source_errors?: null | Record<string, null | string>;
  elapsed?: number;
}

export interface RefreshAllResult {
  brand_meta: RefreshResultItem;
  sales: RefreshResultItem;
  origin: RefreshResultItem;
  status: RefreshStatus;
}

export type RefreshPhaseKey = 'brand_meta' | 'origin' | 'sales';

export interface RefreshProgressEvent {
  phase: RefreshPhaseKey;
  label: string;
  status: 'done' | 'failed' | 'running';
  current: number;
  total: number;
  imported: number;
  detail?: string;
  elapsed?: number;
  source_errors?: null | Record<string, null | string>;
}

export interface RefreshStreamError {
  message: string;
  phase?: RefreshPhaseKey;
}

export interface RefreshStreamHandlers {
  onProgress?: (event: RefreshProgressEvent) => void;
  onDone?: (result: RefreshAllResult) => void;
  onError?: (error: RefreshStreamError) => void;
}

const { apiURL } = useAppConfig(import.meta.env, import.meta.env.PROD);
const STREAM_URL = `${apiURL}/v1/admin/data/refresh/stream`;
const REFRESH_STREAM_IDLE_TIMEOUT_MS = 300_000;

export function refreshAllDataStream(
  handlers: RefreshStreamHandlers,
): AbortController {
  return streamPost<RefreshProgressEvent, RefreshAllResult, RefreshStreamError>(
    STREAM_URL,
    handlers,
    { idleTimeoutMs: REFRESH_STREAM_IDLE_TIMEOUT_MS },
  );
}
