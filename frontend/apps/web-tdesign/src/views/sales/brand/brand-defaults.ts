import { parse } from 'yaml';

import brandDefaultsYaml from './brand-defaults.yaml?raw';

interface BrandDefaultsFile {
  defaultSelectedBrands?: unknown;
}

function readDefaultBrandNames(max: number): string[] {
  const data = parse(brandDefaultsYaml) as BrandDefaultsFile;
  const list = data.defaultSelectedBrands;
  if (!Array.isArray(list)) {
    return [];
  }
  return list.map(String).filter(Boolean).slice(0, max);
}

/** 自模块加载时解析 YAML，最多 3 个（与下拉 max 一致） */
export const DEFAULT_SELECTED_BRAND_NAMES = readDefaultBrandNames(3);
