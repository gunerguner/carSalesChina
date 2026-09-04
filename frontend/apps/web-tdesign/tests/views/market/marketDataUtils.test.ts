import type { RawSalesRecord } from '#/api/market';

import { beforeEach, describe, expect, it, vi } from 'vitest';

import { getMarketRawApi } from '#/api/market';
import { itemAt, mustGet } from '#tests/testUtils';

import {
  buildMarketSeriesCache,
  calcMonthlyDetail,
  calcMonthlyTrend,
  calcQuarterlyTrend,
  calcYearlyTrend,
  EMPTY_SERIES_CACHE,
  fetchMarketRawData,
} from '#/views/market/marketDataUtils';

vi.mock('#/api/market', async () => {
  const actual =
    await vi.importActual<typeof import('#/api/market')>('#/api/market');
  return { ...actual, getMarketRawApi: vi.fn() };
});

function rec(
  year: number,
  month: number,
  sales: number,
  levelType: 'all' | 'bev' | 'nev' = 'all',
  dataType: 'export' | 'production' | 'retail' = 'retail',
): RawSalesRecord {
  return { year, month, sales, level_type: levelType, data_type: dataType };
}

/** 生成整年 1..12 月的行，销量由 salesFn(month) 决定 */
function fullYear(
  year: number,
  salesFn: (month: number) => number,
): RawSalesRecord[] {
  return Array.from({ length: 12 }, (_, i) => rec(year, i + 1, salesFn(i + 1)));
}

const retailAll = (year: number, salesFn: (month: number) => number) =>
  fullYear(year, salesFn);

describe('buildMarketSeriesCache', () => {
  it('按 level::data_type 分组并聚合', () => {
    const raw = [
      ...retailAll(2023, (m) => m),
      ...retailAll(2024, (m) => m),
      // 另一序列：retail::nev
      rec(2024, 1, 50, 'nev'),
      rec(2024, 2, 70, 'nev'),
    ];
    const cacheMap = buildMarketSeriesCache(raw);
    expect([...cacheMap.keys()].toSorted()).toEqual([
      'all::retail',
      'nev::retail',
    ]);

    const cache = mustGet(cacheMap, 'all::retail');
    expect(cache.sortedYears).toEqual([2023, 2024]);
    expect(cache.maxYear).toBe(2024);
    expect(cache.monthlySalesMap.get('2023-12')).toBe(12);
    expect(cache.monthlySalesMap.get('2024-01')).toBe(1);
    // 季度：2023 Q1 = 1+2+3 = 6；2024 Q4 = 10+11+12 = 33
    expect(cache.quarterSalesMap.get('2023-1')).toBe(6);
    expect(cache.quarterSalesMap.get('2024-4')).toBe(33);
    // 年度总量 78
    expect(cache.yearSalesMap.get(2023)).toBe(78);
    expect(cache.maxMonthByYear.get(2023)).toBe(12);
    // 季度键排序跨年正确：2023-4 早于 2024-1
    expect(cache.sortedQuarterKeys).toEqual([
      '2023-1',
      '2023-2',
      '2023-3',
      '2023-4',
      '2024-1',
      '2024-2',
      '2024-3',
      '2024-4',
    ]);
    expect(cache.sortedRows).toEqual([
      ...retailAll(2023, (m) => m),
      ...retailAll(2024, (m) => m),
    ]);
  });

  it('输入乱序时按年月排序', () => {
    const raw = [rec(2024, 2, 2), rec(2023, 12, 12), rec(2024, 1, 1)];
    const cache = mustGet(buildMarketSeriesCache(raw), 'all::retail');
    expect(cache.sortedRows.map((r) => `${r.year}-${r.month}`)).toEqual([
      '2023-12',
      '2024-1',
      '2024-2',
    ]);
  });

  it('空数据返回空 Map', () => {
    expect(buildMarketSeriesCache([]).size).toBe(0);
  });
});

describe('calcMonthlyTrend', () => {
  it('取最近 3 年窗口（含最新年）', () => {
    const raw = [
      rec(2021, 6, 6), // 2021 应被窗口剔除（maxYear=2024 → 窗口 2022 起）
      ...retailAll(2022, (m) => m),
      ...retailAll(2023, (m) => m),
      rec(2024, 1, 1),
      rec(2024, 2, 2),
    ];
    const trend = calcMonthlyTrend(
      mustGet(buildMarketSeriesCache(raw), 'all::retail'),
    );
    expect(trend).toHaveLength(12 + 12 + 2);
    expect(itemAt(trend, 0).year).toBe(2022);
    expect(trend.at(-1)).toMatchObject({ year: 2024, month: 2 });
    expect(trend.every((r) => r.year >= 2022)).toBe(true);
  });

  it('空缓存返回空数组', () => {
    expect(calcMonthlyTrend(EMPTY_SERIES_CACHE)).toEqual([]);
  });
});

describe('calcMonthlyDetail', () => {
  it('计算 MoM（跨年）与 YoY，缺失基准返回 null，最新在前', () => {
    const raw = [
      rec(2023, 1, 200),
      rec(2023, 2, 60),
      rec(2023, 12, 100),
      rec(2024, 1, 150),
      rec(2024, 2, 75),
    ];
    const cache = mustGet(buildMarketSeriesCache(raw), 'all::retail');
    const rows = calcMonthlyDetail(cache);

    // 最新在前
    expect(rows.map((r) => `${r.year}-${r.month}`)).toEqual([
      '2024-2',
      '2024-1',
      '2023-12',
      '2023-2',
      '2023-1',
    ]);

    // 数据为固定 fixture，长度已知（上面已断言 5 行）
    const feb24 = itemAt(rows, 0);
    const jan24 = itemAt(rows, 1);
    const dec23 = itemAt(rows, 2);
    const feb23 = itemAt(rows, 3);
    const jan23 = itemAt(rows, 4);
    // 2024-02: MoM 对比 2024-01 (75 vs 150)，YoY 对比 2023-02 (75 vs 60)
    expect(feb24.momGrowth).toBe(-50);
    expect(feb24.yoyGrowth).toBe(25);
    // 2024-01: MoM 跨年对比 2023-12 (150 vs 100)，YoY 对比 2023-01 (150 vs 200)
    expect(jan24.momGrowth).toBe(50);
    expect(jan24.yoyGrowth).toBe(-25);
    // 2023-12: 上月与去年同期均无数据 → null
    expect(dec23.momGrowth).toBeNull();
    expect(dec23.yoyGrowth).toBeNull();
    // 2023-01: 无环比基准（2022-12 缺失）→ null；YoY 也无 2022-01
    expect(jan23.momGrowth).toBeNull();
    expect(jan23.yoyGrowth).toBeNull();
    // 2023-02: MoM 对比 2023-01 (60 vs 200)；YoY 缺 2022-02
    expect(feb23.momGrowth).toBe(-70);
    expect(feb23.yoyGrowth).toBeNull();

    // key 携带排序下标
    expect(rows.at(-1)?.key).toBe('2023-1-0');
  });
});

describe('calcQuarterlyTrend', () => {
  it('最近 12 个季度、QoQ 跨年、YoY、缺失基准 null', () => {
    // 4 个完整年：季度合计 Q1=6 Q2=15 Q3=24 Q4=33
    const raw = [2021, 2022, 2023, 2024].flatMap((y) => retailAll(y, (m) => m));
    const cache = mustGet(buildMarketSeriesCache(raw), 'all::retail');
    const rows = calcQuarterlyTrend(cache);

    expect(rows).toHaveLength(12); // 16 个季度只留最近 12
    expect(rows[0]).toMatchObject({ year: 2022, quarter: 1 });
    expect(rows.at(-1)).toMatchObject({ year: 2024, quarter: 4 });

    // Q1 的 QoQ 基准为上年 Q4：2022Q1(6) vs 2021Q4(33)
    expect(itemAt(rows, 0).qoqGrowth).toBe(-81.82);
    // YoY: 2022Q1 vs 2021Q1 → 6 vs 6
    expect(itemAt(rows, 0).yoyGrowth).toBe(0);
    // 2024Q4(33) vs 2024Q3(24)
    expect(rows.at(-1)?.qoqGrowth).toBe(37.5);
  });

  it('空缓存返回空数组', () => {
    expect(calcQuarterlyTrend(EMPTY_SERIES_CACHE)).toEqual([]);
  });
});

describe('calcYearlyTrend', () => {
  it('完整年用全年同比；最新不完整年用去年同期累计对比', () => {
    const raw = [
      ...retailAll(2022, (m) => m), // 78，完整年
      ...retailAll(2023, (m) => m * 2), // 156，完整年
      rec(2024, 1, 10), // 最新年只有 1-2 月（部分年）
      rec(2024, 2, 20),
    ];
    const cache = mustGet(buildMarketSeriesCache(raw), 'all::retail');
    const rows = calcYearlyTrend(cache);

    expect(rows.map((r) => r.year)).toEqual([2022, 2023, 2024]);
    // 固定 3 行 fixture
    const y2022 = itemAt(rows, 0);
    const y2023 = itemAt(rows, 1);
    const y2024 = itemAt(rows, 2);

    expect(y2022.sales).toBe(78);
    expect(y2022.yoyGrowth).toBeNull(); // 首年无基准

    expect(y2023.sales).toBe(156);
    expect(y2023.yoyGrowth).toBe(100); // (156-78)/78

    // 部分年：用 2023 年 1-2 月同期累计(2+4=6)对比
    expect(y2024.sales).toBe(30);
    expect(y2024.yoyGrowth).toBe(400); // (30-6)/6
  });

  it('相邻两年中间缺年时 YoY 用前一年而非前两年', () => {
    const raw = [
      ...retailAll(2022, (m) => m),
      rec(2024, 1, 1), // 缺 2023 全年，2024 仍按上年(2022)累计？——
      // 注意：2024 只有 1 月数据且 maxMonth=1 < 12 → 部分年逻辑，基准为 sumMonthsUpTo(2023, 1)=0 → 非法基准 → null
    ];
    const cache = mustGet(buildMarketSeriesCache(raw), 'all::retail');
    const rows = calcYearlyTrend(cache);
    const y2024 = itemAt(rows, rows.length - 1);
    expect(y2024.yoyGrowth).toBeNull();
  });

  it('空缓存返回空数组', () => {
    expect(calcYearlyTrend(EMPTY_SERIES_CACHE)).toEqual([]);
  });
});

describe('fetchMarketRawData', () => {
  beforeEach(() => {
    vi.mocked(getMarketRawApi).mockReset();
  });

  it('返回 API 数据', async () => {
    const data = [rec(2024, 1, 1)];
    vi.mocked(getMarketRawApi).mockResolvedValue(data);
    await expect(fetchMarketRawData()).resolves.toEqual(data);
  });

  it('API 返回非数组时兜底为空数组', async () => {
    vi.mocked(getMarketRawApi).mockResolvedValue(
      null as unknown as RawSalesRecord[],
    );
    await expect(fetchMarketRawData()).resolves.toEqual([]);
  });
});
