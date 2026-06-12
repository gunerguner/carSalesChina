import type { DataType, YearMonthRecord } from '#/utils/types';

import { requestClient } from '#/api/request';

export interface BrandTrendAllPeriodsParams {
  brand_names: string;
  data_type?: DataType;
}

export interface BrandMetaItem {
  brand_id: number;
  brand_name: string;
}

export interface BrandTrendMonthlyRecord extends YearMonthRecord {
  sales: number;
}

export interface BrandTrendAllPeriodsRecord {
  brand_name: string;
  monthly_data: BrandTrendMonthlyRecord[];
}

export function getBrandMetaAllApi() {
  return requestClient.get<BrandMetaItem[]>('/v1/brands/meta/all');
}

export function getBrandTrendAllPeriodsApi(params: BrandTrendAllPeriodsParams) {
  return requestClient.get<BrandTrendAllPeriodsRecord[]>(
    '/v1/brands/trend-all-periods',
    { params },
  );
}
