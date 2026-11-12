import { preferences } from '@vben/preferences';

/** 在 computed 内调用，建立主题 mode 响应式依赖，切换 light/dark 时重建 option */
export function trackThemeMode(): void {
  void preferences.theme.mode;
}
