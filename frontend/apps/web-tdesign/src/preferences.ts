import { defineOverridesPreferences } from '@vben/preferences';

export const overridesPreferences = defineOverridesPreferences({
  app: {
    name: import.meta.env.VITE_APP_TITLE,
    defaultHomePath: '/market-sales',
  },
  theme: {
    mode: 'auto',
  },
  widget: {
    themeToggle: false,
  },
});
