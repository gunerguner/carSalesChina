import type { BrandTrendAllPeriodsRecord } from '#/api/brand';

import { itemAt } from '#tests/testUtils';
import { beforeEach, describe, expect, it, vi } from 'vitest';

import { getBrandTrendAllPeriodsApi } from '#/api/brand';
import { useBrandData } from '#/views/brand/useBrandData';

vi.mock('#/api/brand', async () => {
  const actual =
    await vi.importActual<typeof import('#/api/brand')>('#/api/brand');
  return { ...actual, getBrandTrendAllPeriodsApi: vi.fn() };
});

function month(year: number, m: number, sales: number) {
  return { year, month: m, sales };
}

/** 生成整年 1..12 月，销量由 salesFn(month) 决定 */
function fullYear(year: number, salesFn: (m: number) => number) {
  return Array.from({ length: 12 }, (_, i) => month(year, i + 1, salesFn(i + 1)));
}

function brand(
  name: string,
  monthly: BrandTrendAllPeriodsRecord['monthly_data'],
): BrandTrendAllPeriodsRecord {
  return { brand_name: name, monthly_data: monthly };
}

describe('useBrandData', () => {
  beforeEach(() => {
    vi.mocked(getBrandTrendAllPeriodsApi).mockReset();
    const { dataType, granularity, selectedBrands } = useBrandData();
    selectedBrands.value = [];
    granularity.value = 'recentYear';
    dataType.value = 'retail';
  });

  async function loadBrands(records: BrandTrendAllPeriodsRecord[]) {
    vi.mocked(getBrandTrendAllPeriodsApi).mockResolvedValue(records);
    const api = useBrandData();
    api.selectedBrands.value = records.map((r) => r.brand_name);
    await api.fetchRawData(true);
    return api;
  }

  describe('monthlySeries', () => {
    it('窗口裁剪到近 12 月，缺失月补 0，逐月 YoY', async () => {
      // 最新月 2024-03 → 窗口 2023-04..2024-03；2023-01 在窗外应剔除
      const records = [
        brand('甲', [
          month(2023, 1, 999),
          month(2023, 3, 80),
          month(2023, 4, 100),
          month(2024, 3, 120),
        ]),
      ];
      const { activeSeries, granularity } = await loadBrands(records);
      granularity.value = 'recentYear';

      const series = itemAt(activeSeries.value, 0);
      expect(series.points).toHaveLength(12);
      expect(itemAt(series.points, 0).time).toBe('2023-04');
      expect(itemAt(series.points, 11).time).toBe('2024-03');

      // 窗口内无数据的月补 0
      const apr23 = itemAt(series.points, 0);
      expect(apr23.sales).toBe(100);
      expect(apr23.yoyGrowth).toBeNull(); // 缺 2022-04

      const mar24 = itemAt(series.points, 11);
      expect(mar24.sales).toBe(120);
      expect(mar24.yoyGrowth).toBe(50); // vs 2023-03 (80)

      // 2024-01/02 缺失 → 0
      const jan24 = series.points.find((p) => p.time === '2024-01');
      expect(jan24?.sales).toBe(0);
      expect(series.points.some((p) => p.time === '2023-01')).toBe(false);
    });

    it('recentTwoYears 取近 24 个月', async () => {
      const records = [
        brand('甲', [
          ...fullYear(2022, (m) => m),
          ...fullYear(2023, (m) => m),
          month(2024, 1, 10),
          month(2024, 2, 20),
        ]),
      ];
      const { activeSeries, granularity } = await loadBrands(records);
      granularity.value = 'recentTwoYears';

      const points = itemAt(activeSeries.value, 0).points;
      expect(points).toHaveLength(24);
      expect(itemAt(points, 0).time).toBe('2022-03');
      expect(itemAt(points, 23).time).toBe('2024-02');
    });
  });

  describe('yearlySeries', () => {
    it('最新不完整年用去年同期累计作 YoY 基准', async () => {
      const records = [
        brand('甲', [
          ...fullYear(2022, (m) => m), // 78
          ...fullYear(2023, (m) => m * 2), // 156
          month(2024, 1, 10),
          month(2024, 2, 20),
        ]),
      ];
      const { activeSeries, granularity } = await loadBrands(records);
      granularity.value = 'yearly';

      const points = itemAt(activeSeries.value, 0).points;
      expect(points.map((p) => p.time)).toEqual(['2022', '2023', '2024']);

      const y2022 = itemAt(points, 0);
      expect(y2022.sales).toBe(78);
      expect(y2022.yoyGrowth).toBeNull();

      const y2023 = itemAt(points, 1);
      expect(y2023.sales).toBe(156);
      expect(y2023.yoyGrowth).toBe(100);

      // 部分年：基准 = 2023 年 1-2 月 (2+4=6)
      const y2024 = itemAt(points, 2);
      expect(y2024.sales).toBe(30);
      expect(y2024.yoyGrowth).toBe(400);
    });
  });

  describe('timeLabels', () => {
    it('取各品牌时间点并集并排序', async () => {
      const records = [
        brand('甲', [month(2024, 1, 10), month(2024, 3, 30)]),
        brand('乙', [month(2024, 2, 20), month(2024, 3, 25)]),
      ];
      const { granularity, timeLabels } = await loadBrands(records);
      granularity.value = 'recentYear';

      // 最新月 2024-03 → 近 12 月窗口；并集含两端品牌出现过的标签
      expect(timeLabels.value).toContain('2024-01');
      expect(timeLabels.value).toContain('2024-02');
      expect(timeLabels.value).toContain('2024-03');
      expect(timeLabels.value).toEqual([...timeLabels.value].toSorted());
    });
  });
});
