import { formatNumberOrDash, formatSalesAxisLabel } from './number-utils';

export function getEmptyChartOption(text: string) {
  return {
    animation: false,
    title: {
      text,
      left: 'center',
      top: 'center',
      textStyle: { color: '#999', fontSize: 14 },
    },
    xAxis: { type: 'category' as const, data: [] },
    yAxis: { type: 'value' as const },
    series: [],
  };
}

export { formatSalesAxisLabel };

export function lineSeriesTooltipFormatter(params: any): string {
  const arr = Array.isArray(params) ? params : [params];
  if (arr.length === 0) return '';
  const head = arr[0];
  const label = head.axisValueLabel ?? head.name ?? '';
  const body = arr
    .map((p: any) => {
      const v = formatNumberOrDash(Math.round(Number(p.value)));
      return `${p.marker}${p.seriesName}: ${v}`;
    })
    .join('<br/>');
  return `${label}<br/>${body}`;
}
