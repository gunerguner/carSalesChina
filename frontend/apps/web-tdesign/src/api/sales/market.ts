import { requestClient } from '#/api/request';

export interface MarketOverviewParams {
  year: number;
  month: number;
  energy_type?: string;
  data_type?: 'production' | 'retail' | 'wholesale';
}

export interface MarketTrendParams {
  energy_type?: string;
  years?: number;
  granularity?: 'monthly' | 'yearly';
  data_type?: 'production' | 'retail' | 'wholesale';
}

export interface MarketYearlyParams {
  year: number;
  energy_type?: string;
  data_type?: 'production' | 'retail' | 'wholesale';
}

export interface MarketByEnergyTypeParams {
  year: number;
  month: number;
  data_type?: 'production' | 'retail' | 'wholesale';
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

export function getMarketByEnergyTypeApi(params: MarketByEnergyTypeParams) {
  return requestClient.get('/v1/market/byEnergyType', { params });
}
