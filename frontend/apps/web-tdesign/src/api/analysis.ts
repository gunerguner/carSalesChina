import type {
  AnalysisGranularity,
  OriginShareKey,
  YearMonthRecord,
} from '#/utils/types';

import { requestClient } from '#/api/request';

export interface NevShareTrendRecord extends YearMonthRecord {
  nev_penetration_rate: number;
  nev_sales: number;
  total_sales: number;
}

export interface NevBreakdownRecord extends YearMonthRecord {
  bev_ratio: number;
  bev_sales: number;
}

export type OriginShareTrendRecord = Record<OriginShareKey, number> &
  YearMonthRecord;

export interface AnalysisTrendParams {
  granularity?: AnalysisGranularity;
}

export function getNevShareTrendApi(params?: AnalysisTrendParams) {
  return requestClient.get<NevShareTrendRecord[]>(
    '/v1/analysis/nev-share/trend',
    {
      params,
    },
  );
}

export function getNevBreakdownApi(params?: AnalysisTrendParams) {
  return requestClient.get<NevBreakdownRecord[]>('/v1/analysis/nev-breakdown', {
    params,
  });
}

export function getOriginShareTrendApi(params?: AnalysisTrendParams) {
  return requestClient.get<OriginShareTrendRecord[]>(
    '/v1/analysis/origin-share/trend',
    { params },
  );
}
