import { requestClient } from '#/api/request';

export interface BrandRankingParams {
  year: number;
  month: number;
  energy_type?: string;
  data_type?: 'production' | 'retail' | 'wholesale';
  top_n?: number;
}

export interface BrandRankingYearlyParams {
  year: number;
  energy_type?: string;
  data_type?: 'production' | 'retail' | 'wholesale';
  top_n?: number;
}

export interface BrandCompareParams {
  brand_names: string;
  year: number;
  month: number;
  data_type?: 'production' | 'retail' | 'wholesale';
}

export interface BrandCompareTrendParams {
  brand_names: string;
  energy_type?: string;
  data_type?: 'production' | 'retail' | 'wholesale';
  granularity?: 'monthly' | 'yearly';
}

export interface BrandTrendParams {
  brandName: string;
  energy_type?: string;
  data_type?: 'production' | 'retail' | 'wholesale';
  granularity?: 'monthly' | 'yearly';
}

export function getBrandRankingApi(params: BrandRankingParams) {
  return requestClient.get('/v1/brands/ranking', { params });
}

export function getBrandRankingYearlyApi(params: BrandRankingYearlyParams) {
  return requestClient.get('/v1/brands/ranking/yearly', { params });
}

export function getBrandCompareApi(params: BrandCompareParams) {
  return requestClient.get('/v1/brands/compare', { params });
}

export function getBrandCompareTrendApi(params: BrandCompareTrendParams) {
  return requestClient.get('/v1/brands/compare/trend', { params });
}

export function getBrandTrendApi(brandName: string, params?: Omit<BrandTrendParams, 'brandName'>) {
  return requestClient.get(`/v1/brands/${brandName}/trend`, { params });
}
