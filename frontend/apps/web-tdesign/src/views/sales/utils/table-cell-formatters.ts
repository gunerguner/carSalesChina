import {
  formatNumberOrDash,
  formatPercentOrDash,
} from './number-utils';

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
