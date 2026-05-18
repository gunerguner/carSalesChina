import { h } from 'vue';

export function formatPercentOrDash(
  value: null | number | undefined,
  digits = 2,
): string {
  return value == null ? '-' : `${value.toFixed(digits)}%`;
}

export function formatNumberOrDash(
  value: null | number | undefined,
  locale?: string,
): string {
  return value == null ? '-' : Number(value).toLocaleString(locale);
}

export function formatSalesAxisLabel(value: number, locale: string): string {
  if (value >= 10_000) {
    return locale === 'zh-CN'
      ? `${(value / 10_000).toFixed(0)}万`
      : `${(value / 1000).toFixed(0)}k`;
  }
  return Number(value).toLocaleString(locale);
}

export function formatNumberCell(
  value: null | number | undefined,
  locale?: string,
): string {
  return formatNumberOrDash(value, locale);
}

export function formatPercentCell(
  value: null | number | undefined,
  digits = 2,
): string {
  return formatPercentOrDash(value, digits);
}

export function growthColor(val: null | number | undefined): string {
  if (val == null) return '#999';
  if (val > 0) return '#ef4444';
  if (val < 0) return '#22c55e';
  return '#666';
}

export function growthPercentText(val: null | number | undefined): string {
  return formatPercentOrDash(val, 2);
}

/** TDesign table `cell`: colored growth % from row `${key}Color` / `${key}Text` (see `growthTableRowFields`). */
export function growthTableCell(key: string) {
  return (_: unknown, { row }: { row: Record<string, string> }) =>
    h('span', { style: { color: row[`${key}Color`], fontWeight: 500 } }, row[`${key}Text`]);
}

export function growthTableRowFields(
  key: string,
  value: null | number | undefined,
): Record<string, string> {
  return { [`${key}Color`]: growthColor(value), [`${key}Text`]: growthPercentText(value) };
}
