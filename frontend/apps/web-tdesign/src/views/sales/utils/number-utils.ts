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
      : `${(value / 1_000).toFixed(0)}k`;
  }
  return Number(value).toLocaleString(locale);
}
