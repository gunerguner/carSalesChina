import { requestClient } from '#/api/request';

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

const STREAM_PATH = '/v1/admin/data/refresh/stream';

function createMessageHandler(handlers: RefreshStreamHandlers) {
  let buffer = '';
  return (chunk: string) => {
    buffer += chunk;
    const frames = buffer.split('\n\n');
    buffer = frames.pop() ?? '';

    frames.forEach((frame) => {
      const event = /^event:\s*(\w+)/m.exec(frame)?.[1];
      const data = /^data:\s*(.+)$/m.exec(frame)?.[1];
      if (!event || !data) return;

      const payload: unknown = JSON.parse(data);
      switch (event) {
        case 'done': {
          handlers.onDone?.(payload as RefreshAllResult);
          break;
        }
        case 'error': {
          handlers.onError?.(payload as RefreshStreamError);
          break;
        }
        case 'progress': {
          handlers.onProgress?.(payload as RefreshProgressEvent);
          break;
        }
      }
    });
  };
}

export function refreshAllDataStream(
  handlers: RefreshStreamHandlers,
  signal?: AbortSignal,
) {
  return requestClient.postSSE(STREAM_PATH, undefined, {
    credentials: 'include',
    signal,
    onMessage: createMessageHandler(handlers),
  });
}
