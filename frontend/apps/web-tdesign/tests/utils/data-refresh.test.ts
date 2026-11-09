import { describe, expect, it, vi } from 'vitest';

import {
  emitDataRefresh,
  getDataRefreshEpoch,
  offDataRefresh,
  onDataRefresh,
} from '#/utils/data-refresh';

describe('data-refresh pub/sub', () => {
  it('订阅后 emit 触发', () => {
    const handler = vi.fn();
    onDataRefresh(handler);
    emitDataRefresh();
    expect(handler).toHaveBeenCalledTimes(1);
    offDataRefresh(handler);
  });

  it('emit 触发所有订阅者', () => {
    const a = vi.fn();
    const b = vi.fn();
    onDataRefresh(a);
    onDataRefresh(b);
    emitDataRefresh();
    expect(a).toHaveBeenCalledTimes(1);
    expect(b).toHaveBeenCalledTimes(1);
    offDataRefresh(a);
    offDataRefresh(b);
  });

  it('退订后不再触发', () => {
    const handler = vi.fn();
    onDataRefresh(handler);
    offDataRefresh(handler);
    emitDataRefresh();
    expect(handler).not.toHaveBeenCalled();
  });

  it('退订未订阅的 handler 不抛错', () => {
    expect(() => offDataRefresh(() => {})).not.toThrow();
  });

  it('每次 emit 递增刷新代数', () => {
    const before = getDataRefreshEpoch();
    emitDataRefresh();
    expect(getDataRefreshEpoch()).toBe(before + 1);
  });
});
