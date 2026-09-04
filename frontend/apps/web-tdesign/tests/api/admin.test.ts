import { describe, expect, it, vi } from 'vitest';

import { createMessageHandler } from '#/api/admin';

vi.mock('#/api/request', () => ({
  requestClient: {
    postSSE: vi.fn(),
  },
}));

describe('createMessageHandler', () => {
  it('解析完整 progress/done 帧', () => {
    const onProgress = vi.fn();
    const onDone = vi.fn();
    const onError = vi.fn();
    const handle = createMessageHandler({ onDone, onError, onProgress });

    handle(
      'event: progress\ndata: {"phase":"sales","status":"running"}\n\n' +
        'event: done\ndata: {"status":"success"}\n\n',
    );

    expect(onProgress).toHaveBeenCalledWith(
      expect.objectContaining({ phase: 'sales', status: 'running' }),
    );
    expect(onDone).toHaveBeenCalledWith(
      expect.objectContaining({ status: 'success' }),
    );
    expect(onError).not.toHaveBeenCalled();
  });

  it('不完整帧留在 buffer，下一 chunk 补齐后再派发', () => {
    const onProgress = vi.fn();
    const handle = createMessageHandler({ onProgress });

    handle('event: progress\ndata: {"phase":"origin"');
    expect(onProgress).not.toHaveBeenCalled();

    handle(',"status":"running"}\n\n');
    expect(onProgress).toHaveBeenCalledWith(
      expect.objectContaining({ phase: 'origin', status: 'running' }),
    );
  });

  it('error 事件走 onError；未知事件忽略', () => {
    const onError = vi.fn();
    const onProgress = vi.fn();
    const handle = createMessageHandler({ onError, onProgress });

    handle(
      'event: error\ndata: {"message":"timeout"}\n\n' +
        'event: ping\ndata: {"ok":true}\n\n' +
        'event: progress\n\n',
    );

    expect(onError).toHaveBeenCalledWith(
      expect.objectContaining({ message: 'timeout' }),
    );
    expect(onProgress).not.toHaveBeenCalled();
  });
});
