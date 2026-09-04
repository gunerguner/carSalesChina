import type { ECOption } from '@vben/plugins/echarts';

import { describe, expect, it } from 'vitest';

import {
  buildLineChartOption,
  buildStackedAreaChartOption,
  emptyChartIfNoData,
  getEmptyChartOption,
} from '#/utils/chart';
import { itemAt } from '#tests/testUtils';

type TooltipFormatter = (params: unknown) => string;

function tooltipFormatterOf(option: ECOption): TooltipFormatter {
  const tooltip = option.tooltip as unknown as {
    formatter?: (params: unknown) => string;
  };
  return tooltip.formatter as TooltipFormatter;
}

describe('getEmptyChartOption / emptyChartIfNoData', () => {
  it('空图含标题文案与关闭动画', () => {
    const option = getEmptyChartOption('暂无数据');
    expect(option.animation).toBe(false);
    expect((option.title as { text: string }).text).toBe('暂无数据');
    expect(option.series).toEqual([]);
  });

  it('数据为空时返回空图，否则 undefined', () => {
    const empty = emptyChartIfNoData([], '暂无数据');
    expect(empty).toBeDefined();
    expect(empty).toMatchObject({ title: { text: '暂无数据' } });
    expect(emptyChartIfNoData([1], '暂无数据')).toBeUndefined();
  });
});

describe('buildLineChartOption', () => {
  const params = {
    series: [
      { data: [1, null, 3], name: '零售' },
      { data: [2, 4, 6], name: '出口' },
    ],
    xData: ['2024-01', '2024-02', '2024-03'],
  };

  it('映射 xData/series，动画关闭', () => {
    const option = buildLineChartOption(params);
    expect(option.animation).toBe(false);
    expect((option.xAxis as { data: string[] }).data).toEqual(params.xData);
    const series = option.series as { data: (null | number)[]; name: string }[];
    expect(series.map((s) => s.name)).toEqual(['零售', '出口']);
    expect(itemAt(series, 0).data).toEqual([1, null, 3]);
  });

  it('series emphasis.focus 为 none（禁止 hover 淡化其它系列）', () => {
    const option = buildLineChartOption(params);
    const series = option.series as {
      emphasis: { disabled: boolean; focus: string };
    }[];
    for (const item of series) {
      expect(item.emphasis.focus).toBe('none');
      expect(item.emphasis.disabled).toBe(true);
    }
  });

  it('value 轴 zh-CN 用“万”缩写', () => {
    const option = buildLineChartOption({ ...params, locale: 'zh-CN' });
    const yAxis = option.yAxis as {
      axisLabel?: { formatter?: (v: number) => string };
    };
    const formatter = yAxis.axisLabel?.formatter;
    expect(formatter).toBeTypeOf('function');
    expect(formatter?.(20_000)).toBe('2万');
    expect(formatter?.(200)).toBe('200');
  });

  it('value 轴 en-US 用 k 缩写', () => {
    const option = buildLineChartOption({ ...params, locale: 'en-US' });
    const yAxis = option.yAxis as {
      axisLabel?: { formatter?: (v: number) => string };
    };
    const formatter = yAxis.axisLabel?.formatter;
    expect(formatter?.(20_000)).toBe('20k');
    expect(formatter?.(500)).toBe('500');
  });

  it('percent 轴 label 为 {value}%', () => {
    const option = buildLineChartOption({
      ...params,
      yAxisType: 'percent',
    });
    const yAxis = option.yAxis as {
      axisLabel: { formatter: string };
      max: number;
    };
    expect(yAxis.axisLabel.formatter).toBe('{value}%');
    expect(yAxis.max).toBe(100); // 默认封顶 100
  });

  it('percentMaxCap < 100 时 max 为动态函数', () => {
    const option = buildLineChartOption({
      ...params,
      percentMaxCap: 80,
      yAxisType: 'percent',
    });
    const yAxis = option.yAxis as { max: (v: { max: number }) => number };
    expect(yAxis.max({ max: 90 })).toBe(80); // min(ceil(90*1.2)=108, 80)
    expect(yAxis.max({ max: 20 })).toBe(24);
  });

  it('默认 tooltip formatter 拼接多系列并四舍五入', () => {
    const option = buildLineChartOption({ ...params, locale: 'en-US' });
    const html = tooltipFormatterOf(option)([
      {
        axisValueLabel: '2024-01',
        marker: '■',
        seriesName: '零售',
        value: 1499.6,
      },
      { marker: '■', seriesName: '出口', value: null },
    ]);
    expect(html).toContain('2024-01');
    expect(html).toContain('零售: 1,500');
    expect(html).toContain('出口: -');
  });

  it('tooltip trigger 为 axis', () => {
    const option = buildLineChartOption(params);
    expect((option.tooltip as { trigger: string }).trigger).toBe('axis');
  });
});

describe('buildStackedAreaChartOption', () => {
  const params = {
    legend: { data: ['自主', '德系'] },
    series: [
      { color: '#111111', data: [60, 70], name: '自主' },
      { color: '#222222', data: [25, 30], name: '德系' },
    ],
    xData: ['2024-01', '2024-02'],
  };

  it('series 全部 stack=total', () => {
    const option = buildStackedAreaChartOption(params);
    const series = option.series as {
      emphasis: { focus: string };
      stack: string;
    }[];
    expect(series.every((s) => s.stack === 'total')).toBe(true);
    expect(series.every((s) => s.emphasis.focus === 'none')).toBe(true);
  });

  it('y 轴默认封顶 100 且为百分比', () => {
    const option = buildStackedAreaChartOption(params);
    const yAxis = option.yAxis as {
      axisLabel: { formatter: string };
      max: number;
    };
    expect(yAxis.max).toBe(100);
    expect(yAxis.axisLabel.formatter).toBe('{value}%');
  });

  it('tooltip 显示一位小数的百分比', () => {
    const option = buildStackedAreaChartOption(params);
    const html = tooltipFormatterOf(option)([
      {
        axisValueLabel: '2024-01',
        marker: '■',
        seriesName: '自主',
        value: 33.3333,
      },
    ]);
    expect(html).toContain('自主: 33.3%');
    expect(html).not.toContain('33.33');
  });
});
