import type { VNode } from 'vue';

import { describe, expect, it } from 'vitest';

import {
  growthTableCell,
  salesYoyTableCell,
  tableNumberCell,
} from '#/utils/render';

describe('tableNumberCell', () => {
  it('取行字段并格式化，nil → 占位符', () => {
    const cell = tableNumberCell('sales');
    expect(cell(null, { row: { sales: 300 } })).toBe('300');
    expect(cell(null, { row: { sales: null } })).toBe('-');
    expect(cell(null, { row: {} })).toBe('-');
  });

  it('支持后缀（百分比）', () => {
    const cell = tableNumberCell('rate', '%');
    expect(cell(null, { row: { rate: 12.5 } })).toBe('12.5%');
  });
});

describe('salesYoyTableCell', () => {
  it('无同比时仅返回销量文本', () => {
    const cell = salesYoyTableCell('sales', 'yoy');
    const result = cell(null, { row: { sales: 300, yoy: null } });
    expect(result).toBe('300');
  });

  it('有同比时渲染带颜色的复合 VNode', () => {
    const cell = salesYoyTableCell('sales', 'yoy');
    const vnode = cell(null, { row: { sales: 300, yoy: 10.5 } }) as VNode;
    expect(vnode.type).toBe('span');
    const children = vnode.children as (string | VNode)[];
    expect(children[0]).toBe('300');
    const inner = children[1] as VNode;
    expect((inner.props as { style: { color: string } }).style.color).toBe(
      '#ef4444',
    );
    expect(inner.children).toBe('（+10.5%）');
  });
});

describe('growthTableCell', () => {
  it('按行内 Color/Text 字段渲染着色 span', () => {
    const vnode = growthTableCell('yoyGrowth')(null, {
      row: { yoyGrowthColor: '#22c55e', yoyGrowthText: '-8%' },
    }) as VNode;
    expect(vnode.type).toBe('span');
    expect((vnode.props as { style: { color: string } }).style.color).toBe(
      '#22c55e',
    );
    expect(vnode.children).toBe('-8%');
  });
});
