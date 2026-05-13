import { defineOverridesPreferences } from '@vben/preferences';

export const overridesPreferences = defineOverridesPreferences({
  app: {
    name: import.meta.env.VITE_APP_TITLE,
    defaultHomePath: '/market-sales',
  },
  tabbar: {
    enable: false,
  },
  theme: {
    mode: 'auto',
  },
  widget: {
    refresh: false,
    themeToggle: false,
  },
});
