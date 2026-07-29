import { requestClient } from '#/api/request';

export interface SSEHandlers<
  TProgress = unknown,
  TDone = unknown,
  TError extends { message: string } = { message: string },
> {
  onOpen?: () => void;
  onProgress?: (data: TProgress) => void;
  onDone?: (data: TDone) => void;
  /** Transport errors are `{ message }`; stream error events are `TError`. */
  onError?: (data: TError | { message: string }) => void;
  onPing?: () => void;
}

export interface StreamPostOptions {
  params?: Record<string, string>;
  signal?: AbortSignal;
  idleTimeoutMs?: number;
  headers?: Record<string, string>;
}

function parseSSEFrame(raw: string): null | { data: string; event: string } {
  const lines = raw.split('\n');
  let event = 'message';
  const dataLines: string[] = [];

  lines.forEach((line) => {
    if (line.startsWith('event:')) {
      event = line.slice(6).trim();
      return;
    }
    if (line.startsWith('data:')) {
      dataLines.push(line.slice(5).trim());
    }
  });

  if (dataLines.length === 0) {
    return null;
  }

  return { event, data: dataLines.join('\n') };
}

export function streamPost<
  TProgress = unknown,
  TDone = unknown,
  TError extends { message: string } = { message: string },
>(
  url: string,
  handlers: SSEHandlers<TProgress, TDone, TError>,
  options: StreamPostOptions = {},
): AbortController {
  const controller = new AbortController();
  const idleTimeoutMs = options.idleTimeoutMs ?? 30_000;
  const search = options.params
    ? `?${new URLSearchParams(options.params).toString()}`
    : '';

  let idleTimer: null | ReturnType<typeof setTimeout> = null;
  let receivedTerminalEvent = false;
  let buffer = '';
  let opened = false;

  const emitError = (error: TError | { message: string }) => {
    handlers.onError?.(error);
  };

  const clearIdleTimer = () => {
    if (idleTimer) {
      clearTimeout(idleTimer);
      idleTimer = null;
    }
  };

  const resetIdleTimer = () => {
    clearIdleTimer();
    idleTimer = setTimeout(() => {
      controller.abort();
      emitError({ message: '连接超时' });
    }, idleTimeoutMs);
  };

  const dispatchFrame = (event: string, payload: string) => {
    resetIdleTimer();
    let parsed: unknown = payload;
    if (payload) {
      try {
        parsed = JSON.parse(payload);
      } catch {
        parsed = payload;
      }
    }

    switch (event) {
      case 'done': {
        receivedTerminalEvent = true;
        handlers.onDone?.(parsed as TDone);
        break;
      }
      case 'error': {
        receivedTerminalEvent = true;
        handlers.onError?.(parsed as TError);
        break;
      }
      case 'ping': {
        handlers.onPing?.();
        break;
      }
      case 'progress': {
        handlers.onProgress?.(parsed as TProgress);
        break;
      }
      default: {
        break;
      }
    }
  };

  const processChunk = (content: string) => {
    if (!opened) {
      opened = true;
      handlers.onOpen?.();
    }
    buffer += content;
    const frames = buffer.split('\n\n');
    buffer = frames.pop() ?? '';

    frames.forEach((frame) => {
      const trimmed = frame.trim();
      if (!trimmed) return;
      const parsed = parseSSEFrame(trimmed);
      if (!parsed) return;
      dispatchFrame(parsed.event, parsed.data);
    });
  };

  const flushTail = () => {
    const tail = buffer.trim();
    if (!tail) return;
    const parsed = parseSSEFrame(tail);
    if (parsed) {
      dispatchFrame(parsed.event, parsed.data);
    }
  };

  resetIdleTimer();

  requestClient
    .postSSE(`${url}${search}`, undefined, {
      credentials: 'include',
      headers: options.headers,
      signal: options.signal ?? controller.signal,
      onMessage: processChunk,
      onEnd: () => {
        flushTail();
        if (!receivedTerminalEvent) {
          emitError({ message: '连接意外断开' });
        }
        clearIdleTimer();
      },
    })
    .catch((error: unknown) => {
      clearIdleTimer();
      if (controller.signal.aborted) {
        return;
      }
      const message = error instanceof Error ? error.message : '网络请求失败';
      emitError({ message });
    });

  return controller;
}
