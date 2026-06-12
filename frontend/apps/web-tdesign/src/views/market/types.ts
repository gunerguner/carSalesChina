export type MarketPeriodKind = 'monthly' | 'quarterly' | 'yearly';

/** UI filter value for market period tabs (same literals as `MarketPeriodKind`). */
export type MarketPeriodGranularity = MarketPeriodKind;

/** Discriminated union helper for market chart/table builders keyed by period. */
export type MarketPeriodInput<TMap extends Record<MarketPeriodKind, unknown>> = {
  [K in MarketPeriodKind]: { data: TMap[K][]; kind: K };
}[MarketPeriodKind];
