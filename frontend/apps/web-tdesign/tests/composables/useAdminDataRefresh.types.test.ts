import type {
  RefreshAllResult,
  RefreshProgressEvent,
  RefreshStreamError,
} from '#/api/admin';

import { describe, expect, it } from 'vitest';

import {
  applyProgressEvent,
  applyStreamDone,
  applyStreamError,
  createInitialProgressState,
  PHASE_ORDER,
} from '#/composables/useAdminDataRefresh.types';

function progressEvent(
  partial: Partial<RefreshProgressEvent>,
): RefreshProgressEvent {
  return {
    phase: 'brand_meta',
    label: '品牌元数据',
    status: 'running',
    current: 0,
    total: 1,
    imported: 0,
    ...partial,
  };
}

function doneResult(
  partial?: Partial<RefreshAllResult['sales']>,
): RefreshAllResult {
  return {
    brand_meta: {
      imported: 2,
      total: 2,
      status: 'success',
    },
    sales: { imported: 9, total: 9, status: 'success', ...partial },
    origin: { imported: 4, total: 4, status: 'success' },
    status: 'success',
  };
}

describe('createInitialProgressState', () => {
  it('所有阶段 pending，整体 idle', () => {
    const state = createInitialProgressState();
    expect(PHASE_ORDER).toEqual(['brand_meta', 'sales', 'origin']);
    expect(state.overallStatus).toBe('idle');
    expect(state.completedCount).toBe(0);
    expect(state.errorMessage).toBeNull();
    expect(state.totalPhases).toBe(3);
    expect(state.phases.brand_meta.status).toBe('pending');
    expect(state.phases.sales.status).toBe('pending');
    expect(state.phases.origin.status).toBe('pending');
  });
});

describe('applyProgressEvent', () => {
  it('running 事件更新阶段字段且整体 running', () => {
    let state = createInitialProgressState();
    state = applyProgressEvent(
      state,
      progressEvent({
        phase: 'sales',
        label: '销量数据',
        current: 3,
        total: 10,
        detail: '品牌销量 3/10',
      }),
    );
    const sales = state.phases.sales;
    expect(sales.status).toBe('running');
    expect(sales.label).toBe('销量数据');
    expect(sales.current).toBe(3);
    expect(sales.total).toBe(10);
    expect(sales.detail).toBe('品牌销量 3/10');
    expect(state.overallStatus).toBe('running');
    expect(state.completedCount).toBe(0);
  });

  it('done 计入 completedCount', () => {
    let state = createInitialProgressState();
    state = applyProgressEvent(
      state,
      progressEvent({
        phase: 'brand_meta',
        status: 'done',
        current: 1,
        total: 1,
        imported: 1,
      }),
    );
    expect(state.phases.brand_meta.status).toBe('done');
    expect(state.completedCount).toBe(1);
  });

  it('failed 计入 completedCount 并保留 source_errors', () => {
    let state = createInitialProgressState();
    state = applyProgressEvent(
      state,
      progressEvent({
        phase: 'origin',
        status: 'failed',
        source_errors: { origin: 'akshare 挂了' },
      }),
    );
    expect(state.phases.origin.status).toBe('failed');
    expect(state.completedCount).toBe(1);
    expect(state.phases.origin.source_errors).toEqual({
      origin: 'akshare 挂了',
    });
  });

  it('事件缺字段时保留旧值（label 回退语义）', () => {
    let state = createInitialProgressState();
    state = applyProgressEvent(
      state,
      progressEvent({
        phase: 'origin',
        label: '国别占比',
        current: 2,
        total: 5,
      }),
    );
    // 第二次事件缺 label/current → 应保留上次的 label 与 current
    state = applyProgressEvent(
      state,
      progressEvent({
        phase: 'origin',
        label: '',
        current: undefined as unknown as number,
        total: 5,
      }),
    );
    expect(state.phases.origin.label).toBe('国别占比');
    expect(state.phases.origin.current).toBe(2);
  });
});

describe('applyStreamError', () => {
  it('带 phase 的错误标记该阶段 failed', () => {
    let state = createInitialProgressState();
    state = applyProgressEvent(
      state,
      progressEvent({ phase: 'sales', status: 'running' }),
    );
    const error: RefreshStreamError = { phase: 'sales', message: '连接中断' };
    state = applyStreamError(state, error);
    expect(state.overallStatus).toBe('error');
    expect(state.errorMessage).toBe('连接中断');
    expect(state.phases.sales.status).toBe('failed');
  });

  it('不带 phase 的错误不改动阶段', () => {
    let state = createInitialProgressState();
    state = applyStreamError(state, { message: '意外错误' });
    expect(state.overallStatus).toBe('error');
    expect(state.errorMessage).toBe('意外错误');
    expect(state.phases.sales.status).toBe('pending');
  });
});

describe('applyStreamDone', () => {
  it('按结果回填所有阶段并标记 done', () => {
    let state = createInitialProgressState();
    state = applyProgressEvent(state, progressEvent({ status: 'running' }));
    state = applyStreamDone(state, doneResult());

    expect(state.overallStatus).toBe('done');
    expect(state.completedCount).toBe(3);
    expect(state.errorMessage).toBeNull();
    expect(state.phases.brand_meta.imported).toBe(2);
    expect(state.phases.sales.imported).toBe(9);
    expect(state.phases.origin.imported).toBe(4);
    expect(state.phases.sales.status).toBe('done');
  });

  it('failed 的阶段保持 failed（不被 done 覆盖）', () => {
    let state = createInitialProgressState();
    state = applyProgressEvent(
      state,
      progressEvent({ phase: 'origin', status: 'failed' }),
    );
    const result = doneResult({ status: 'partial_failure' });
    result.origin.status = 'failed';
    state = applyStreamDone(state, result);
    expect(state.phases.origin.status).toBe('failed');
    expect(state.phases.sales.status).toBe('done');
  });
});
