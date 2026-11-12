import type {
  RefreshAllResult,
  RefreshStreamHandlers,
} from '#/api/admin';

import { beforeEach, describe, expect, it, vi } from 'vitest';

import { useAdminDataRefresh } from '#/composables/useAdminDataRefresh';
import { emitDataRefresh } from '#/utils/data-refresh';

const { refreshAllDataStream } = vi.hoisted(() => ({
  refreshAllDataStream: vi.fn(),
}));

vi.mock('#/locales', () => ({
  $t: (key: string) => key,
}));

vi.mock('#/utils/data-refresh', () => ({
  emitDataRefresh: vi.fn(),
}));

vi.mock('#/api/admin', () => ({
  refreshAllDataStream,
}));

const doneResult: RefreshAllResult = {
  brand_meta: { imported: 1, status: 'success', total: 1 },
  origin: { imported: 1, status: 'success', total: 1 },
  sales: { imported: 1, status: 'success', total: 1 },
  status: 'success',
};

describe('useAdminDataRefresh', () => {
  beforeEach(() => {
    refreshAllDataStream.mockReset();
    vi.mocked(emitDataRefresh).mockClear();
  });

  it('401/503 不打开进度浮层，并把服务端文案交回确认框', async () => {
    refreshAllDataStream.mockRejectedValue(
      Object.assign(new Error('密码错误'), { status: 401 }),
    );
    const { progressVisible, refreshAdminData } = useAdminDataRefresh();

    const result = await refreshAdminData('bad');

    expect(result).toEqual({ accepted: false, message: '密码错误' });
    expect(progressVisible.value).toBe(false);
    expect(refreshAllDataStream).toHaveBeenCalledWith(
      expect.any(Object),
      'bad',
      expect.any(AbortSignal),
    );
  });

  it('收到进度后才视为已接受', async () => {
    refreshAllDataStream.mockImplementation(
      async (handlers: RefreshStreamHandlers) => {
        handlers.onProgress?.({
          current: 0,
          imported: 0,
          label: '品牌',
          phase: 'brand_meta',
          status: 'running',
          total: 1,
        });
        handlers.onDone?.(doneResult);
      },
    );
    const { progressVisible, refreshAdminData } = useAdminDataRefresh();

    const result = await refreshAdminData('secret');

    expect(result).toEqual({ accepted: true });
    expect(progressVisible.value).toBe(true);
  });

  it('关闭部分失败结果时刷新页面', async () => {
    refreshAllDataStream.mockImplementation(
      async (handlers: RefreshStreamHandlers) => {
        handlers.onDone?.({
          ...doneResult,
          sales: { imported: 1, status: 'partial_failure', total: 1 },
          status: 'partial_failure',
        });
      },
    );
    const { closeProgressModal, progressState, refreshAdminData } =
      useAdminDataRefresh();

    await refreshAdminData('secret');
    expect(progressState.value.overallStatus).toBe('partial');
    closeProgressModal();

    expect(emitDataRefresh).toHaveBeenCalledOnce();
  });

  it('关闭失败结果时不刷新页面', async () => {
    refreshAllDataStream.mockImplementation(
      async (handlers: RefreshStreamHandlers) => {
        handlers.onError?.({ message: '连接中断' });
      },
    );
    const { closeProgressModal, progressState, refreshAdminData } =
      useAdminDataRefresh();

    await refreshAdminData('secret');
    expect(progressState.value.overallStatus).toBe('error');
    closeProgressModal();

    expect(emitDataRefresh).not.toHaveBeenCalled();
  });
});
