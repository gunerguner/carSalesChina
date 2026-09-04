import { describe, expect, it } from 'vitest';

import {
  BRAND_LINE_PALETTE_INDICES,
  DEFAULT_TABLE_PROPS,
  getChartPaletteColor,
  getChartTheme,
  getOriginShareColor,
  growthStyle,
  growthTableRowFields,
  readCssVar,
} from '#/utils/style';

describe('readCssVar', () => {
  it('读取已定义的 CSS 变量', () => {
    document.documentElement.style.setProperty('--test-var-x', 'rgb(1, 2, 3)');
    expect(readCssVar('--test-var-x', 'fallback')).toBe('rgb(1, 2, 3)');
  });

  it('未定义时回退 fallback', () => {
    expect(readCssVar('--never-defined-var', 'fallback')).toBe('fallback');
  });
});

describe('growthStyle', () => {
  it('null → 中性灰与占位符', () => {
    const { color, text } = growthStyle(null);
    expect(color).toBe('#64748b');
    expect(text).toBe('-');
  });

  it('正增长 → 红色 + 前缀（中国惯例涨红）', () => {
    const { color, text } = growthStyle(12.5);
    expect(color).toBe('#ef4444');
    expect(text).toBe('+12.5%');
  });

  it('负增长 → 绿色', () => {
    const { color, text } = growthStyle(-8);
    expect(color).toBe('#22c55e');
    expect(text).toBe('-8%');
  });

  it('零增长无正号', () => {
    expect(growthStyle(0).text).toBe('0%');
  });
});

describe('growthTableRowFields', () => {
  it('追加按 key 命名的 Color/Text 字段', () => {
    expect(growthTableRowFields('yoyGrowth', 10)).toEqual({
      yoyGrowthColor: '#ef4444',
      yoyGrowthText: '+10%',
    });
    expect(growthTableRowFields('yoyGrowth', null).yoyGrowthText).toBe('-');
  });
});

describe('图表取色', () => {
  it('getChartTheme 提供全部主题回退值', () => {
    const theme = getChartTheme();
    expect(theme.axis).toBe('#64748b');
    expect(theme.tooltipBg).toBe('#ffffff');
    expect(theme.tooltipText).toBe('#1e293b');
  });

  it('palette 按 index 循环', () => {
    expect(getChartPaletteColor(0)).toBe('#475569');
    expect(getChartPaletteColor(1)).toBe('#35827a');
    expect(getChartPaletteColor(8)).toBe('#475569'); // 循环回第一个
  });

  it('品牌对比取色为间隔索引', () => {
    expect(BRAND_LINE_PALETTE_INDICES).toEqual([0, 2, 4, 6]);
  });

  it('国别键映射到 palette 索引', () => {
    expect(getOriginShareColor('domestic')).toBe(getChartPaletteColor(0));
    expect(getOriginShareColor('german')).toBe(getChartPaletteColor(1));
    expect(getOriginShareColor('french')).toBe(getChartPaletteColor(6));
  });
});

describe('DEFAULT_TABLE_PROPS', () => {
  it('表格壳层固定配置', () => {
    expect(DEFAULT_TABLE_PROPS).toEqual({
      bordered: true,
      rowKey: 'key',
      size: 'small',
      stripe: true,
    });
  });
});
