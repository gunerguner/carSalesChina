import { requestClient } from '#/api/request';

export interface NevShareTrendParams {
  energy_type?: string;
  data_type?: 'production' | 'retail' | 'wholesale';
  granularity?: 'monthly' | 'yearly';
}

export interface NevShareOverviewParams {
  year: number;
  month: number;
  data_type?: 'production' | 'retail' | 'wholesale';
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
  return requestClient.get('/v1/analysis/nev-share/trend', { params });
}

export function getNevShareOverviewApi(params: NevShareOverviewParams) {
  return requestClient.get('/v1/analysis/nev-share/overview', { params });
}

export function getNevBreakdownApi(params?: NevBreakdownParams) {
  return requestClient.get('/v1/analysis/nev-breakdown', { params });
}

export function getOriginShareTrendApi(params?: OriginShareTrendParams) {
  return requestClient.get('/v1/analysis/origin-share/trend', { params });
}
