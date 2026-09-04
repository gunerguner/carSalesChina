import { describe, expect, it } from 'vitest';

import {
  formatMonthPeriod,
  formatQuarterPeriod,
  formatYearPeriod,
  getLocalizedMonthLabels,
  priorYearMonthKey,
  toMonthKey,
  toYearMonthSortKey,
  toYearQuarterSortKey,
} from '#/utils/period';

describe('toMonthKey', () => {
  it('月份补零', () => {
    expect(toMonthKey(2024, 1)).toBe('2024-01');
    expect(toMonthKey(2024, 12)).toBe('2024-12');
  });
});

describe('priorYearMonthKey', () => {
  it('跨年减一年', () => {
    expect(priorYearMonthKey('2024-01')).toBe('2023-01');
    expect(priorYearMonthKey('2023-12')).toBe('2022-12');
  });
});

describe('周期格式化', () => {
  it('月度 zh-CN / 其他', () => {
    expect(formatMonthPeriod(2024, 3, 'zh-CN')).toBe('2024年3月');
    expect(formatMonthPeriod(2024, 3, 'en-US')).toBe('2024-03');
  });

  it('季度 zh-CN / 其他', () => {
    expect(formatQuarterPeriod(2024, 2, 'zh-CN')).toBe('2024年Q2');
    expect(formatQuarterPeriod(2024, 2, 'en-US')).toBe('2024 Q2');
  });

  it('年度 zh-CN / 其他', () => {
    expect(formatYearPeriod(2024, 'zh-CN')).toBe('2024年');
    expect(formatYearPeriod(2024, 'en-US')).toBe('2024');
  });
});

describe('getLocalizedMonthLabels', () => {
  it('产出 12 个月份', () => {
    expect(getLocalizedMonthLabels('en-US')).toHaveLength(12);
    expect(getLocalizedMonthLabels('zh-CN')).toHaveLength(12);
  });

  it('英文为缩写标签', () => {
    const labels = getLocalizedMonthLabels('en-US');
    expect(labels[0]).toBe('Jan');
    expect(labels[11]).toBe('Dec');
  });

  it('中文含“月”', () => {
    const labels = getLocalizedMonthLabels('zh-CN');
    expect(labels[0]).toContain('月');
    expect(labels[11]).toContain('月');
  });
});

describe('排序键', () => {
  it('年月复合排序键', () => {
    expect(toYearMonthSortKey(2024, 2)).toBe(202_402);
    expect(toYearMonthSortKey(2023, 12)).toBeLessThan(
      toYearMonthSortKey(2024, 1),
    );
  });

  it('年季复合排序键', () => {
    expect(toYearQuarterSortKey(2024, 4)).toBe(20_244);
    expect(toYearQuarterSortKey(2023, 4)).toBeLessThan(
      toYearQuarterSortKey(2024, 1),
    );
  });
});
