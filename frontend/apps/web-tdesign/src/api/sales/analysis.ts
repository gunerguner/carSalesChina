import { requestClient } from '#/api/request';

export interface AnalysisPeriodRecord {
  month: number;
  year: number;
}

export interface NevShareTrendRecord extends AnalysisPeriodRecord {
  nev_penetration_rate: number;
  nev_sales: number;
  total_sales: number;
}

export interface NevBreakdownRecord extends AnalysisPeriodRecord {
  bev_ratio: number;
  bev_sales: number;
}

export interface OriginShareTrendRecord extends AnalysisPeriodRecord {
  american: number;
  domestic: number;
  european: number;
  french: number;
  german: number;
  japanese: number;
  korean: number;
}

export interface AnalysisTrendParams {
  granularity?: 'monthly' | 'yearly';
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
