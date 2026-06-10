export function toMonthKey(year: number, month: number): string {
  return `${year}-${String(month).padStart(2, '0')}`;
}

export function formatMonthPeriod(
  year: number,
  month: number,
  locale: string,
): string {
  return locale === 'zh-CN' ? `${year}年${month}月` : toMonthKey(year, month);
}

export function formatQuarterPeriod(
  year: number,
  quarter: number,
  locale: string,
): string {
  return locale === 'zh-CN' ? `${year}年Q${quarter}` : `${year} Q${quarter}`;
}

export function formatYearPeriod(year: number, locale: string): string {
  return locale === 'zh-CN' ? `${year}年` : String(year);
}

export function getLocalizedMonthLabels(locale: string): string[] {
  const monthFormatter = new Intl.DateTimeFormat(locale, { month: 'short' });
  return Array.from({ length: 12 }, (_, i) =>
    monthFormatter.format(new Date(2000, i, 1)),
  );
}

export function toYearMonthSortKey(year: number, month: number): number {
  return year * 100 + month;
}

export function toYearQuarterSortKey(year: number, quarter: number): number {
  return year * 10 + quarter;
}
