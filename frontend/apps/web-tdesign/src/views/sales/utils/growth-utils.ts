import { formatPercentOrDash } from './number-utils';

export function growthColor(val: null | number | undefined): string {
  if (val == null) return '#999';
  if (val > 0) return '#ef4444';
  if (val < 0) return '#22c55e';
  return '#666';
}

export function growthPercentText(val: null | number | undefined): string {
  return formatPercentOrDash(val, 2);
}
