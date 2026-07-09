export interface SSEHandlers<
  TProgress = unknown,
  TDone = unknown,
  TError = unknown,
> {
  onOpen?: () => void;
  onProgress?: (data: TProgress) => void;
  onDone?: (data: TDone) => void;
  onError?: (data: TError) => void;
  onPing?: () => void;
}

export interface StreamPostOptions {
  params?: Record<string, string>;
  signal?: AbortSignal;
  idleTimeoutMs?: number;
  headers?: Record<string, string>;
}

function getCsrfToken(): string | undefined {
  const match = document.cookie.match(/(?:^|;\s*)csrf_token=([^;]*)/);
  return match?.[1];
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
  TError = unknown,
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
  const csrfToken = getCsrfToken();

  let idleTimer: null | ReturnType<typeof setTimeout> = null;

  const resetIdleTimer = () => {
    if (idleTimer) {
      clearTimeout(idleTimer);
    }
    idleTimer = setTimeout(() => {
      controller.abort();
      handlers.onError?.({ message: '连接超时' } as TError);
    }, idleTimeoutMs);
  };

  const clearIdleTimer = () => {
    if (idleTimer) {
      clearTimeout(idleTimer);
      idleTimer = null;
    }
  };

  const run = async () => {
    resetIdleTimer();
    let receivedTerminalEvent = false;

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

    try {
      const response = await fetch(`${url}${search}`, {
        credentials: 'include',
        headers: {
          Accept: 'text/event-stream',
          ...(csrfToken ? { 'X-CSRF-Token': csrfToken } : {}),
          ...options.headers,
        },
        method: 'POST',
        signal: options.signal ?? controller.signal,
      });

      if (!response.ok) {
        let message = `请求失败 (${response.status})`;
        try {
          const body = await response.json();
          message = body.message || message;
        } catch {
          // ignore parse error
        }
        receivedTerminalEvent = true;
        handlers.onError?.({ message } as TError);
        return;
      }

      handlers.onOpen?.();

      const reader = response.body?.getReader();
      if (!reader) {
        receivedTerminalEvent = true;
        handlers.onError?.({ message: '无法读取响应流' } as TError);
        return;
      }

      const decoder = new TextDecoder();
      let buffer = '';
      let streamDone = false;

      while (!streamDone) {
        const { done, value } = await reader.read();
        streamDone = done;
        if (done) {
          break;
        }

        buffer += decoder.decode(value, { stream: true });
        const frames = buffer.split('\n\n');
        buffer = frames.pop() ?? '';

        frames.forEach((frame) => {
          const trimmed = frame.trim();
          if (!trimmed) return;
          const parsed = parseSSEFrame(trimmed);
          if (!parsed) return;
          dispatchFrame(parsed.event, parsed.data);
        });
      }

      const tail = buffer.trim();
      if (tail) {
        const parsed = parseSSEFrame(tail);
        if (parsed) {
          dispatchFrame(parsed.event, parsed.data);
        }
      }

      if (!receivedTerminalEvent) {
        handlers.onError?.({ message: '连接意外断开' } as TError);
      }
    } catch (error) {
      if (controller.signal.aborted) {
        return;
      }
      const message = error instanceof Error ? error.message : '网络请求失败';
      handlers.onError?.({ message } as TError);
    } finally {
      clearIdleTimer();
    }
  };

  run().catch(() => {
    // run() 内部已处理错误回调
  });

  return controller;
}
