import type { OriginShareKey } from '#/utils/types';

import { ORIGIN_KEYS } from '#/utils/types';

import { formatOrDash, isNil } from './format';

export function readCssVar(name: string, fallback: string): string {
  if (typeof document === 'undefined') return fallback;
  const value = getComputedStyle(document.documentElement)
    .getPropertyValue(name)
    .trim();
  return value || fallback;
}

/** 看板 TDesign Table 默认壳层 props */
export const DEFAULT_TABLE_PROPS = {
  bordered: true,
  rowKey: 'key',
  size: 'small',
  stripe: true,
} as const;

export function growthStyle(val: null | number): {
  color: string;
  text: string;
} {
  const muted = readCssVar('--tone-muted', '#64748b');
  if (isNil(val)) return { color: muted, text: '-' };
  let color = muted;
  if (val > 0) {
    color = readCssVar('--tone-destructive', '#ef4444');
  } else if (val < 0) {
    color = readCssVar('--tone-success', '#22c55e');
  }
  return { color, text: `${val > 0 ? '+' : ''}${formatOrDash(val, '%')}` };
}

export function growthTableRowFields(
  key: string,
  value: null | number,
): Record<string, string> {
  const { color, text } = growthStyle(value);
  return { [`${key}Color`]: color, [`${key}Text`]: text };
}

const CHART_VAR_KEYS = [
  '--chart-1',
  '--chart-2',
  '--chart-3',
  '--chart-4',
  '--chart-5',
  '--chart-6',
  '--chart-7',
  '--chart-8',
] as const;

const CHART_FALLBACKS = [
  '#475569',
  '#35827a',
  '#c47a1a',
  '#7c5cbf',
  '#c4475a',
  '#3d8b5a',
  '#2f7ea8',
  '#c45c2a',
] as const;

/** 品牌对比线色：按色相间隔取色，避免相邻线过于接近 */
export const BRAND_LINE_PALETTE_INDICES = [0, 2, 4, 6] as const;

export function getChartTheme() {
  return {
    axis: readCssVar('--chart-axis', '#64748b'),
    grid: readCssVar('--chart-grid', '#e2e8f0'),
    pointer: readCssVar('--chart-pointer', '#475569'),
    tooltipBg: readCssVar('--chart-tooltip-bg', '#ffffff'),
    tooltipBorder: readCssVar('--chart-tooltip-border', '#e2e8f0'),
    tooltipText: readCssVar('--chart-tooltip-text', '#1e293b'),
  };
}

export function getChartPaletteColor(index: number): string {
  const key = CHART_VAR_KEYS[index % CHART_VAR_KEYS.length] ?? '--chart-1';
  return readCssVar(
    key,
    CHART_FALLBACKS[index % CHART_FALLBACKS.length] ?? '#475569',
  );
}

export function getOriginShareColor(key: OriginShareKey): string {
  const index = ORIGIN_KEYS.indexOf(key);
  return getChartPaletteColor(Math.max(index, 0));
}
