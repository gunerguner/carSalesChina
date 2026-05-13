import { requestClient } from '#/api/request';

export interface BrandTrendAllPeriodsParams {
  brand_names: string;
  data_type?: 'production' | 'retail';
}

export interface BrandMetaItem {
  brand_id: number;
  brand_name: string;
}

export function getBrandMetaAllApi() {
  return requestClient.get<BrandMetaItem[]>('/v1/brands/meta/all');
}

export function getBrandTrendAllPeriodsApi(params: BrandTrendAllPeriodsParams) {
  return requestClient.get('/v1/brands/trend-all-periods', { params });
}
