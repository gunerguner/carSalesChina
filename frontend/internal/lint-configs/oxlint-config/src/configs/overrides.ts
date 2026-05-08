import type { OxlintConfig } from 'oxlint';

const overrides: OxlintConfig = {
  overrides: [
    {
      files: ['*.d.ts', '**/*.d.ts'],
      rules: {
        'import/no-unassigned-import': 'off',
        'typescript/triple-slash-reference': 'off',
      },
    },
    {
      files: ['packages/@core/base/shared/src/utils/inference.ts'],
      rules: {
        'vue/prefer-import-from-vue': 'off',
      },
    },
    {
      files: ['packages/@core/ui-kit/menu-ui/src/sub-menu.vue'],
      rules: {
        'import/no-self-import': 'off',
      },
    },
    {
      files: [
        'scripts/**/*.js',
        'scripts/**/*.cjs',
        'scripts/**/*.mjs',
        'scripts/**/*.jsx',
        'scripts/**/*.ts',
        'scripts/**/*.cts',
        'scripts/**/*.mts',
        'scripts/**/*.tsx',
        'internal/**/*.js',
        'internal/**/*.cjs',
        'internal/**/*.mjs',
        'internal/**/*.jsx',
        'internal/**/*.ts',
        'internal/**/*.cts',
        'internal/**/*.mts',
        'internal/**/*.tsx',
      ],
      rules: {
        'no-console': 'off',
        'unicorn/no-process-exit': 'off',
      },
    },
  ],
};

export { overrides };
