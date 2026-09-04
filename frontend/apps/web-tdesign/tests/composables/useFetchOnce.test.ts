import { ref } from 'vue';

import { beforeEach, describe, expect, it, vi } from 'vitest';

import {
  createFetchOnceController,
  createKeyedFetchController,
  fetchArrayInto,
  LOAD_FAILED_I18N_KEY,
} from '#/composables/useFetchOnce';

describe('fetchArrayInto', () => {
  it('把数组写入 ref', async () => {
    const target = ref<number[]>([]);
    await fetchArrayInto(target, async () => [1, 2]);
    expect(target.value).toEqual([1, 2]);
  });

  it('非数组写入空数组', async () => {
    const target = ref<number[]>([9]);
    await fetchArrayInto(target, async () => 'not-array');
    expect(target.value).toEqual([]);
  });
});

describe('createFetchOnceController', () => {
  beforeEach(() => {
    vi.spyOn(console, 'error').mockImplementation(() => {});
  });

  it('首次成功后默认跳过，force 才重跑', async () => {
    const task = vi.fn().mockResolvedValue(undefined);
    const ctrl = createFetchOnceController();
    await ctrl.execute(false, task);
    await ctrl.execute(false, task);
    expect(task).toHaveBeenCalledTimes(1);
    await ctrl.execute(true, task);
    expect(task).toHaveBeenCalledTimes(2);
  });

  it('进行中的请求去重', async () => {
    const hold: { resolve?: () => void } = {};
    const task = vi.fn(
      () =>
        new Promise<void>((resolve) => {
          hold.resolve = resolve;
        }),
    );
    const ctrl = createFetchOnceController();
    const first = ctrl.execute(false, task);
    const second = ctrl.execute(false, task);
    expect(task).toHaveBeenCalledTimes(1);
    hold.resolve?.();
    await Promise.all([first, second]);
  });

  it('失败写入 i18n key 且不标记已拉取', async () => {
    const ctrl = createFetchOnceController();
    await ctrl.execute(false, async () => {
      throw new Error('network');
    });
    expect(ctrl.error.value).toBe(LOAD_FAILED_I18N_KEY);
    expect(ctrl.loading.value).toBe(false);

    const task = vi.fn().mockResolvedValue(undefined);
    await ctrl.execute(false, task);
    expect(task).toHaveBeenCalledTimes(1);
  });
});

describe('createKeyedFetchController', () => {
  beforeEach(() => {
    vi.spyOn(console, 'error').mockImplementation(() => {});
  });

  it('空 key 清空 data', async () => {
    const ctrl = createKeyedFetchController({
      fetch: async () => 'x',
      getKey: () => '',
      isEmptyKey: (key) => key.length === 0,
    });
    ctrl.data.value = 'stale';
    await ctrl.execute();
    expect(ctrl.data.value).toBeNull();
    expect(ctrl.loading.value).toBe(false);
  });

  it('命中缓存直接返回', async () => {
    const fetch = vi.fn(async (key: string) => `data-${key}`);
    const currentKey = { value: 'a' };
    const ctrl = createKeyedFetchController({
      fetch,
      getKey: () => currentKey.value,
    });
    await ctrl.execute();
    expect(ctrl.data.value).toBe('data-a');
    await ctrl.execute();
    expect(fetch).toHaveBeenCalledTimes(1);
  });

  it('force 跳过缓存', async () => {
    const fetch = vi.fn(async (key: string) => `data-${key}`);
    const ctrl = createKeyedFetchController({
      fetch,
      getKey: () => 'a',
    });
    await ctrl.execute();
    await ctrl.execute(true);
    expect(fetch).toHaveBeenCalledTimes(2);
  });

  it('丢弃过期响应', async () => {
    const hold: { resolveA?: (value: string) => void } = {};
    const fetch = vi.fn((key: string) => {
      if (key === 'a') {
        return new Promise<string>((resolve) => {
          hold.resolveA = resolve;
        });
      }
      return Promise.resolve(`data-${key}`);
    });
    const currentKey = { value: 'a' };
    const ctrl = createKeyedFetchController({
      fetch,
      getKey: () => currentKey.value,
    });
    const stale = ctrl.execute();
    currentKey.value = 'b';
    await ctrl.execute();
    hold.resolveA?.('stale-a');
    await stale;
    expect(ctrl.data.value).toBe('data-b');
  });

  it('失败写入 i18n key 并清空 data', async () => {
    const ctrl = createKeyedFetchController({
      fetch: async () => {
        throw new Error('boom');
      },
      getKey: () => 'a',
    });
    await ctrl.execute();
    expect(ctrl.error.value).toBe(LOAD_FAILED_I18N_KEY);
    expect(ctrl.data.value).toBeNull();
  });
});
