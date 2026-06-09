import { parse } from 'yaml';

import brandDefaultsYaml from '#/brand-defaults.yaml?raw';
import { isNil, notNil } from '#/utils/format';

interface BrandDefaultsFile {
  defaultSelectedBrands?: unknown;
  quickFilters?: unknown;
}

export interface BrandQuickFilter {
  id: string;
  labelKey: string;
  action?: 'clear';
  brands?: string[];
}

/** 品牌销量对比最多可选数量（与下拉 max、后端校验一致） */
export const MAX_BRAND_COMPARE = 4;

const parsedDefaults = parse(brandDefaultsYaml) as BrandDefaultsFile;

function readStringList(value: unknown): string[] {
  if (!Array.isArray(value)) {
    return [];
  }
  return value.map(String).filter(Boolean);
}

function readDefaultBrandNames(max: number): string[] {
  return readStringList(parsedDefaults.defaultSelectedBrands).slice(0, max);
}

function readQuickFilters(): BrandQuickFilter[] {
  const list = parsedDefaults.quickFilters;
  if (!Array.isArray(list)) {
    return [];
  }
  return list
    .map((item): BrandQuickFilter | null => {
      if (isNil(item) || typeof item !== 'object') {
        return null;
      }
      const row = item as Record<string, unknown>;
      const id = String(row.id ?? '').trim();
      const labelKey = String(row.labelKey ?? '').trim();
      if (!id || !labelKey) {
        return null;
      }
      const action = row.action === 'clear' ? 'clear' : undefined;
      const brands = readStringList(row.brands);
      if (action !== 'clear' && brands.length === 0) {
        return null;
      }
      return {
        id,
        labelKey,
        ...(action ? { action } : {}),
        ...(brands.length > 0 ? { brands } : {}),
      };
    })
    .filter((item): item is BrandQuickFilter => notNil(item));
}

/** 从配置名列表中筛出元数据存在的品牌并截断至 max */
export function resolveBrandNames(
  names: string[],
  allowed: Set<string>,
  max = MAX_BRAND_COMPARE,
): string[] {
  return names.filter((name) => allowed.has(name)).slice(0, max);
}

/** 自模块加载时解析 YAML，最多 MAX_BRAND_COMPARE 个 */
export const DEFAULT_SELECTED_BRAND_NAMES =
  readDefaultBrandNames(MAX_BRAND_COMPARE);

/** 快筛配置（按钮文案走 labelKey → i18n） */
export const BRAND_QUICK_FILTERS = readQuickFilters();
