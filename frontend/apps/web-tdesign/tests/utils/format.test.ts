import { describe, expect, it } from 'vitest';

import {
  calcGrowthPercent,
  ensureArray,
  formatOrDash,
  isNil,
} from '#/utils/format';

describe('isNil', () => {
  it('识别 null/undefined', () => {
    expect(isNil(null)).toBe(true);
    expect(isNil(undefined)).toBe(true);
  });

  it('拒绝其他值', () => {
    expect(isNil(0)).toBe(false);
    expect(isNil('')).toBe(false);
    expect(isNil(Number.NaN)).toBe(false);
  });
});

describe('ensureArray', () => {
  it('原样返回数组', () => {
    const arr = [1, 2];
    expect(ensureArray<number>(arr)).toBe(arr);
  });

  it('非数组返回空数组', () => {
    expect(ensureArray(null)).toEqual([]);
    expect(ensureArray(undefined)).toEqual([]);
    expect(ensureArray({ length: 2 })).toEqual([]);
    expect(ensureArray('abc')).toEqual([]);
  });
});

describe('calcGrowthPercent', () => {
  it('正常增长（四舍五入两位）', () => {
    expect(calcGrowthPercent(120, 100)).toBe(20);
    expect(calcGrowthPercent(3, 9)).toBe(-66.67);
  });

  it('base 为 null/0/负数时返回 null', () => {
    expect(calcGrowthPercent(10, null)).toBeNull();
    expect(calcGrowthPercent(10, undefined as unknown as null)).toBeNull();
    expect(calcGrowthPercent(10, 0)).toBeNull();
    expect(calcGrowthPercent(10, -5)).toBeNull();
  });

  it('base 大于 0 时恒返回数字（含 0 增长）', () => {
    expect(calcGrowthPercent(100, 100)).toBe(0);
  });
});

describe('formatOrDash', () => {
  it('nil 渲染为占位符', () => {
    expect(formatOrDash(null)).toBe('-');
    expect(formatOrDash(undefined as unknown as null)).toBe('-');
  });

  it('追加后缀', () => {
    expect(formatOrDash(12.5, '万辆')).toBe('12.5万辆');
  });

  it('按 locale 分组格式化', () => {
    expect(formatOrDash(1_234_567.8, '', 'en-US')).toBe('1,234,567.8');
  });
});
