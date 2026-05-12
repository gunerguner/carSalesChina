import { requestClient } from '#/api/request';

export interface RawSalesRecord {
  data_type: 'production' | 'retail';
  level_type: 'all' | 'bev' | 'nev';
  month: number;
  sales: number;
  year: number;
}

export function getMarketRawApi(): Promise<RawSalesRecord[]> {
  return requestClient.get('/v1/market/raw');
}
