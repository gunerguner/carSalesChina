import type { OxlintConfig } from 'oxlint';

const vue: OxlintConfig = {
  rules: {
    'vue/prefer-import-from-vue': 'error',
    'vue/no-reserved-component-names': 'off',
  },
};

export { vue };
