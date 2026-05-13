import { requestClient } from '#/api/request';

export interface AnalysisPeriodRecord {
  month: number;
  year: number;
}

export interface NevShareTrendRecord extends AnalysisPeriodRecord {
  nev_penetration_rate: null | number;
  nev_sales: null | number;
  total_sales: null | number;
}

export interface NevBreakdownRecord extends AnalysisPeriodRecord {
  bev_ratio: null | number;
  bev_sales: null | number;
  hybrid_ratio: null | number;
  phev_ratio: null | number;
}

export interface OriginShareTrendRecord extends AnalysisPeriodRecord {
  american: null | number;
  domestic: null | number;
  european: null | number;
  french: null | number;
  german: null | number;
  japanese: null | number;
  korean: null | number;
}

export interface NevShareTrendParams {
  energy_type?: string;
  data_type?: 'production' | 'retail' | 'wholesale';
  granularity?: 'monthly' | 'yearly';
}

export interface NevBreakdownParams {
  energy_type?: string;
  data_type?: 'production' | 'retail' | 'wholesale';
  granularity?: 'monthly' | 'yearly';
}

export interface OriginShareTrendParams {
  data_type?: 'production' | 'retail' | 'wholesale';
  granularity?: 'monthly' | 'yearly';
}

export function getNevShareTrendApi(params?: NevShareTrendParams) {
  return requestClient.get<NevShareTrendRecord[]>('/v1/analysis/nev-share/trend', {
    params,
  });
}

export function getNevBreakdownApi(params?: NevBreakdownParams) {
  return requestClient.get<NevBreakdownRecord[]>('/v1/analysis/nev-breakdown', {
    params,
  });
}

export function getOriginShareTrendApi(params?: OriginShareTrendParams) {
  return requestClient.get<OriginShareTrendRecord[]>(
    '/v1/analysis/origin-share/trend',
    { params },
  );
}
