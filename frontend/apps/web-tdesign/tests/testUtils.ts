/**
 * 测试辅助函数。
 *
 * 项目 lint 规则（no-non-null-assertion）禁止 `!` 非空断言，而 tsconfig 的
 * noUncheckedIndexedAccess 又让数组/Map 取值带上 undefined——用运行时守卫
 * 在测试中安全解包，两个约束同时满足。
 */

/** 断言数组存在该下标并返回元素（等价于 `arr[i]!`）。 */
export function itemAt<T>(items: readonly T[], index: number): T {
  const item = items[index];
  if (item === undefined) {
    throw new Error(`itemAt: 下标 ${index} 越界（长度 ${items.length}）`);
  }
  return item;
}

/** 断言 Map 存在该键并返回值（等价于 `map.get(k)!`）。 */
export function mustGet<K, V>(map: ReadonlyMap<K, V>, key: K): V {
  const value = map.get(key);
  if (value === undefined) {
    throw new Error(`mustGet: 缺少键 ${String(key)}`);
  }
  return value;
}
