import { defineOverridesPreferences } from '@vben/preferences';

export const overridesPreferences = defineOverridesPreferences({
  app: {
    name: import.meta.env.VITE_APP_TITLE || '中国市场汽车销量',
    defaultHomePath: '/market',
  },
  logo: {
    // lucide:car，白天/暗夜分别用深色与浅色描边，保证对比度
    source: '/logo.svg',
    sourceDark: '/logo-dark.svg',
  },
  tabbar: {
    enable: false,
  },
  theme: {
    builtinType: 'slate',
    mode: 'auto',
    radius: '0.75',
  },
  widget: {
    lockScreen: false,
    refresh: false,
    themeToggle: false,
  },
  footer: {
    enable: true,
    fixed: false,
    height: 56,
  },
  copyright: {
    enable: false,
    settingShow: false,
  },
});
