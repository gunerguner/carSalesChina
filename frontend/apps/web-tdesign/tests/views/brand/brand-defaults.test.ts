import { describe, expect, it } from 'vitest';

import {
  BRAND_QUICK_FILTERS,
  DEFAULT_SELECTED_BRAND_NAMES,
  MAX_BRAND_COMPARE,
  resolveBrandNames,
} from '#/views/brand/brand-defaults';

describe('resolveBrandNames', () => {
  it('过滤不在元数据中的名称，并截断到 MAX_BRAND_COMPARE', () => {
    const allowed = new Set(['丰田', '大众', '日产', '本田', '比亚迪']);
    expect(
      resolveBrandNames(
        ['未知', '比亚迪', '大众', '丰田', '本田', '日产'],
        allowed,
      ),
    ).toEqual(['比亚迪', '大众', '丰田', '本田']);
    expect(MAX_BRAND_COMPARE).toBe(4);
  });

  it('全部非法时返回空数组', () => {
    expect(resolveBrandNames(['无此品牌'], new Set(['比亚迪']))).toEqual([]);
  });
});

describe('DEFAULT_SELECTED_BRAND_NAMES', () => {
  it('从 yaml 解析出非空列表且不超过上限', () => {
    expect(DEFAULT_SELECTED_BRAND_NAMES.length).toBeGreaterThan(0);
    expect(DEFAULT_SELECTED_BRAND_NAMES.length).toBeLessThanOrEqual(
      MAX_BRAND_COMPARE,
    );
    expect(
      DEFAULT_SELECTED_BRAND_NAMES.every((name) => typeof name === 'string'),
    ).toBe(true);
  });
});

describe('BRAND_QUICK_FILTERS', () => {
  it('从 yaml 解析出非空快筛，含 clear 与品牌列表项', () => {
    expect(BRAND_QUICK_FILTERS.length).toBeGreaterThan(0);

    const clear = BRAND_QUICK_FILTERS.find((f) => f.action === 'clear');
    expect(clear).toMatchObject({
      action: 'clear',
      id: expect.any(String),
      labelKey: expect.any(String),
    });

    const brandFilters = BRAND_QUICK_FILTERS.filter((f) => f.action !== 'clear');
    expect(brandFilters.length).toBeGreaterThan(0);
    for (const filter of brandFilters) {
      expect(filter.id).toBeTruthy();
      expect(filter.labelKey).toBeTruthy();
      expect(filter.brands?.length).toBeGreaterThan(0);
    }
  });
});
