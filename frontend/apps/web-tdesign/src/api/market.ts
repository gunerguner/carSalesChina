import type {
  DataType,
  LevelType,
  YearMonthRecord,
} from '#/utils/types';

import { requestClient } from '#/api/request';

export interface RawSalesRecord extends YearMonthRecord {
  data_type: DataType;
  level_type: LevelType;
  sales: number;
}

export function getMarketRawApi(): Promise<RawSalesRecord[]> {
  return requestClient.get('/v1/market/raw');
}
