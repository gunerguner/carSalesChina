import { h } from 'vue';

import { formatOrDash, isNil } from './format';
import { growthStyle } from './style';

/** TDesign table `cell`: formatted number from row field. */
export function tableNumberCell<K extends string>(key: K) {
  return (_: unknown, { row }: { row: Record<string, null | number> }) =>
    formatOrDash(row[key] ?? null);
}

/** TDesign table `cell`: formatted percent from row field. */
export function tablePercentCell<K extends string>(key: K) {
  return (_: unknown, { row }: { row: Record<string, null | number> }) =>
    formatOrDash(row[key] ?? null, '%');
}

/** TDesign table `cell`: "149,985（+10.38%）" with colored YoY from row `${salesKey}` / `${yoyKey}`. */
export function salesYoyTableCell(salesKey: string, yoyKey: string) {
  return (_: unknown, { row }: { row: Record<string, null | number> }) => {
    const sales = row[salesKey] ?? null;
    const yoy = row[yoyKey] ?? null;
    const salesText = formatOrDash(sales);
    if (isNil(yoy)) return salesText;
    const { color, text } = growthStyle(yoy);
    return h('span', [
      salesText,
      h('span', { style: { color, fontWeight: 500 } }, `（${text}）`),
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
