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
  it('null → 占位符，颜色与零增长同属中性', () => {
    const nil = growthStyle(null);
    expect(nil.text).toBe('-');
    expect(nil.color).toBe(growthStyle(0).color);
  });

  it('正增长带 + 前缀，负增长不带 +，且颜色不同', () => {
    const up = growthStyle(12.5);
    const down = growthStyle(-8);
    expect(up.text).toBe('+12.5%');
    expect(down.text).toBe('-8%');
    expect(up.color).not.toBe(down.color);
    expect(up.color).not.toBe(growthStyle(0).color);
  });

  it('零增长无正号', () => {
    expect(growthStyle(0).text).toBe('0%');
  });
});

describe('growthTableRowFields', () => {
  it('追加按 key 命名的 Color/Text 字段', () => {
    const fields = growthTableRowFields('yoyGrowth', 10);
    expect(fields.yoyGrowthText).toBe('+10%');
    expect(fields.yoyGrowthColor).toBeTruthy();
    expect(growthTableRowFields('yoyGrowth', null).yoyGrowthText).toBe('-');
  });
});

describe('图表取色', () => {
  it('getChartTheme 提供必要主题键，且可被 CSS 变量覆盖', () => {
    const theme = getChartTheme();
    expect(theme).toEqual(
      expect.objectContaining({
        axis: expect.any(String),
        tooltipBg: expect.any(String),
        tooltipText: expect.any(String),
      }),
    );
    document.documentElement.style.setProperty('--chart-axis', 'rgb(9, 9, 9)');
    expect(getChartTheme().axis).toBe('rgb(9, 9, 9)');
  });

  it('palette 按 index 循环回绕', () => {
    expect(getChartPaletteColor(8)).toBe(getChartPaletteColor(0));
    expect(getChartPaletteColor(9)).toBe(getChartPaletteColor(1));
    expect(getChartPaletteColor(0)).not.toBe(getChartPaletteColor(1));
  });

  it('品牌对比取色互不相同', () => {
    const colors = BRAND_LINE_PALETTE_INDICES.map((i) => getChartPaletteColor(i));
    expect(new Set(colors).size).toBe(colors.length);
  });

  it('国别键映射到稳定 palette 色', () => {
    expect(getOriginShareColor('domestic')).toBe(getChartPaletteColor(0));
    expect(getOriginShareColor('german')).toBe(getChartPaletteColor(1));
    expect(getOriginShareColor('french')).toBe(getChartPaletteColor(6));
  });
});

describe('DEFAULT_TABLE_PROPS', () => {
  it('提供表格壳层必需字段', () => {
    expect(DEFAULT_TABLE_PROPS.rowKey).toBe('key');
    expect(DEFAULT_TABLE_PROPS.bordered).toBe(true);
    expect(DEFAULT_TABLE_PROPS.stripe).toBe(true);
  });
});
