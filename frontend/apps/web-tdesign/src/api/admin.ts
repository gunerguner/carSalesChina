import { requestClient } from '#/api/request';

const REFRESH_TIMEOUT = 5 * 60 * 1000; // 5 分钟

export function refreshBrandMetaApi() {
  return requestClient.post('/v1/admin/data/refresh/brand-meta', undefined, {
    timeout: REFRESH_TIMEOUT,
  });
}

export function refreshSalesApi() {
  return requestClient.post('/v1/admin/data/refresh/sales', undefined, {
    timeout: REFRESH_TIMEOUT,
  });
}

export function refreshOriginApi() {
  return requestClient.post('/v1/admin/data/refresh/origin', undefined, {
    timeout: REFRESH_TIMEOUT,
  });
}
