import { h } from 'vue';

/** Returns true when value is null or undefined. */
export function isNil(value: unknown): value is null | undefined {
  return value === null || value === undefined;
}

/** Returns true when value is neither null nor undefined. */
export function notNil<T>(value: T): value is NonNullable<T> {
  return value !== null && value !== undefined;
}

export function round2(n: number): number {
  return Math.round(n * 100) / 100;
}

export function calcGrowthPercent(
  current: number,
  base: null | number | undefined,
): null | number {
  if (isNil(base) || base <= 0) {
    return null;
  }
  return round2(((current - base) / base) * 100);
}

export function formatPercentOrDash(
  value: null | number | undefined,
  digits = 2,
): string {
  return isNil(value) ? '-' : `${value.toFixed(digits)}%`;
}

export function formatNumberOrDash(
  value: null | number | undefined,
  locale?: string,
): string {
  return isNil(value) ? '-' : value.toLocaleString(locale);
}

export function formatSalesAxisLabel(value: number, locale: string): string {
  if (value >= 10_000) {
    return locale === 'zh-CN'
      ? `${(value / 10_000).toFixed(0)}万`
      : `${(value / 1000).toFixed(0)}k`;
  }
  return value.toLocaleString(locale);
}

export function growthColor(val: null | number | undefined): string {
  if (isNil(val)) return '#999';
  if (val > 0) return '#ef4444';
  if (val < 0) return '#22c55e';
  return '#666';
}

export function growthPercentText(val: null | number | undefined): string {
  return formatPercentOrDash(val, 2);
}

export function formatSignedGrowthPercent(
  val: null | number | undefined,
  digits = 2,
): string {
  if (isNil(val)) {
    return '-';
  }
  const sign = val > 0 ? '+' : '';
  return `${sign}${val.toFixed(digits)}%`;
}

/** TDesign table `cell`: "149,985（+10.38%）" with colored YoY from row `${salesKey}` / `${yoyKey}`. */
export function salesYoyTableCell(salesKey: string, yoyKey: string) {
  return (
    _: unknown,
    { row }: { row: Record<string, null | number | undefined> },
  ) => {
    const sales = row[salesKey];
    const yoy = row[yoyKey];
    const salesText = isNil(sales) ? '-' : sales.toLocaleString();
    if (isNil(yoy)) {
      return salesText;
    }
    return h('span', [
      salesText,
      h(
        'span',
        { style: { color: growthColor(yoy), fontWeight: 500 } },
        `（${formatSignedGrowthPercent(yoy)}）`,
      ),
    ]);
  };
}

/** TDesign table `cell`: colored growth % from row `${key}Color` / `${key}Text` (see `growthTableRowFields`). */
export function growthTableCell(key: string) {
  return (_: unknown, { row }: { row: Record<string, string> }) =>
    h(
      'span',
      { style: { color: row[`${key}Color`], fontWeight: 500 } },
      row[`${key}Text`],
    );
}

export function growthTableRowFields(
  key: string,
  value: null | number | undefined,
): Record<string, string> {
  return {
    [`${key}Color`]: growthColor(value),
    [`${key}Text`]: growthPercentText(value),
  };
}
