export function isNil(value: unknown): value is null | undefined {
  return value === null || value === undefined;
}

function readSalesCssVar(name: string, fallback: string): string {
  if (typeof document === 'undefined') return fallback;
  const value = getComputedStyle(document.documentElement)
    .getPropertyValue(name)
    .trim();
  return value || fallback;
}

export function calcGrowthPercent(
  current: number,
  base: null | number,
): null | number {
  if (isNil(base) || base <= 0) return null;
  return Math.round(((current - base) / base) * 100 * 100) / 100;
}

export function formatOrDash(
  value: null | number,
  suffix = '',
  locale?: string,
): string {
  if (isNil(value)) return '-';
  return suffix ? `${value}${suffix}` : value.toLocaleString(locale);
}

export function growthStyle(val: null | number): {
  color: string;
  text: string;
} {
  const muted = readSalesCssVar('--sales-muted-foreground', '#64748b');
  if (isNil(val)) return { color: muted, text: '-' };
  let color = muted;
  if (val > 0) {
    color = readSalesCssVar('--sales-destructive', '#ef4444');
  } else if (val < 0) {
    color = readSalesCssVar('--sales-success', '#22c55e');
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
