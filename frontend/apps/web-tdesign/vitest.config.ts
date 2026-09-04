import { fileURLToPath } from 'node:url';

import vue from '@vitejs/plugin-vue';
import { defineConfig } from 'vitest/config';

const srcDir = fileURLToPath(new URL('./src', import.meta.url));
const testsDir = fileURLToPath(new URL('./tests', import.meta.url));

export default defineConfig({
  plugins: [vue()],
  resolve: {
    alias: {
      // 与 package.json imports + tsconfig paths 保持一致
      '#': srcDir,
      '#tests': testsDir,
    },
  },
  test: {
    environment: 'happy-dom',
    include: ['tests/**/*.test.ts'],
    // 每个用例后自动 restore 所有 spy/mock，防止模块级单例状态泄漏
    restoreMocks: true,
    coverage: {
      provider: 'v8',
      reporter: ['text', 'html'],
      // 只统计 TS 逻辑层；Vue SFC 靠组件测试按需覆盖，不设 fail-under
      include: ['src/**/*.ts'],
      exclude: [
        'src/main.ts',
        'src/bootstrap.ts',
        'src/preferences.ts',
        'src/locales/**',
        'src/router/**',
      ],
    },
  },
});
