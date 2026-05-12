import { requestClient } from '#/api/request';

export interface MarketOverviewParams {
  year: number;
  month: number;
  level_type?: string;
  data_type?: 'production' | 'retail';
  date_type?: 'monthly' | 'quarterly' | 'yearly';
}

export interface MarketTrendParams {
  level_type?: string;
  years?: number;
  granularity?: 'monthly' | 'yearly';
  data_type?: 'production' | 'retail';
  date_type?: 'monthly' | 'quarterly' | 'yearly';
}

export interface MarketYearlyParams {
  year: number;
  level_type?: string;
  data_type?: 'production' | 'retail';
  date_type?: 'monthly' | 'quarterly' | 'yearly';
}

export interface RawSalesRecord {
  data_type: 'production' | 'retail';
  level_type: 'all' | 'bev' | 'nev';
  month: number;
  sales: number;
  year: number;
}

export function getMarketOverviewApi(params: MarketOverviewParams) {
  return requestClient.get('/v1/market/overview', { params });
}

export function getMarketTrendApi(params: MarketTrendParams) {
  return requestClient.get('/v1/market/trend', { params });
}

export function getMarketYearlyApi(params: MarketYearlyParams) {
  return requestClient.get('/v1/market/yearly', { params });
}

export function getMarketRawApi(): Promise<RawSalesRecord[]> {
  return requestClient.get('/v1/market/raw');
}