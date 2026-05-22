import { defineOverridesPreferences } from '@vben/preferences';

export const overridesPreferences = defineOverridesPreferences({
  app: {
    name: import.meta.env.VITE_APP_TITLE || '中国市场汽车销量',
    defaultHomePath: '/market-sales',
  },
  tabbar: {
    enable: false,
  },
  theme: {
    mode: 'auto',
  },
  widget: {
    lockScreen: false,
    refresh: false,
    themeToggle: false,
  },
});
