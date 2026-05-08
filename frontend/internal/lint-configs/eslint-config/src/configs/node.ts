import type { Linter } from 'eslint';

import { interopDefault } from '../util';

export async function node(): Promise<Linter.Config[]> {
  const pluginNode = await interopDefault(import('eslint-plugin-n'));

  return [
    {
      plugins: {
        n: pluginNode,
      },
      rules: {
        'n/handle-callback-err': ['error', '^(err|error)$'],
        'n/no-deprecated-api': 'error',
        'n/no-extraneous-import': [
          'error',
          {
            allowModules: [
              'tsdown',
              'unplugin-vue',
              '@vben/vite-config',
              'vite',
              '@vue/test-utils',
            ],
          },
        ],
        'n/no-unsupported-features/es-syntax': [
          'error',
          {
            ignores: [],
            version: '>=20.12.0',
          },
        ],
        'n/prefer-global/buffer': ['error', 'never'],
        'n/prefer-global/process': ['error', 'never'],
        'n/process-exit-as-throw': 'error',
      },
    },
    {
      files: ['docs/**/**'],
      rules: {
        'n/no-extraneous-import': 'off',
        'n/prefer-global/buffer': 'off',
        'n/prefer-global/process': 'off',
      },
    },
    {
      files: [
        'scripts/**/*.?([cm])[jt]s?(x)',
        'internal/**/*.?([cm])[jt]s?(x)',
      ],
      rules: {
        'n/prefer-global/process': 'off',
      },
    },
  ];
}
