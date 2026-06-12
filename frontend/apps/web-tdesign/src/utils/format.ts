export function isNil(value: unknown): value is null | undefined {
  return value === null || value === undefined;
}

export function ensureArray<T>(value: unknown): T[] {
  return Array.isArray(value) ? value : [];
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
