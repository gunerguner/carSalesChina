import { requestClient } from '#/api/request';

const REFRESH_TIMEOUT = 5 * 60 * 1000; // 5 分钟

/** 与后端 import_service 刷新返回值对齐 */
export type AdminDataRefreshStatus = 'failed' | 'partial_failure' | 'success';

export interface RefreshBrandMetaPayload {
  inserted: number;
  status: 'skipped' | 'success';
  total?: number;
  updated?: number;
  reason?: string;
}

export interface RefreshSalesPayload {
  brand_count: number;
  overall_count: number;
  records_count: number;
  status: AdminDataRefreshStatus;
  source_errors: {
    brand: null | string;
    overall: null | string;
  };
}

export interface RefreshOriginPayload {
  origin_count: number;
  records_count: number;
  status: 'failed' | 'success';
  source_errors: { origin: null | string };
}

export function refreshBrandMetaApi() {
  return requestClient.post<RefreshBrandMetaPayload>(
    '/v1/admin/data/refresh/brand-meta',
    undefined,
    {
      timeout: REFRESH_TIMEOUT,
    },
  );
}

export function refreshSalesApi() {
  return requestClient.post<RefreshSalesPayload>(
    '/v1/admin/data/refresh/sales',
    undefined,
    {
      timeout: REFRESH_TIMEOUT,
    },
  );
}

export function refreshOriginApi() {
  return requestClient.post<RefreshOriginPayload>(
    '/v1/admin/data/refresh/origin',
    undefined,
    {
      timeout: REFRESH_TIMEOUT,
    },
  );
}
