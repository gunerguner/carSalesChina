import { defineConfig } from '@vben/vite-config';

/** carSales：关闭 Vben 默认重型构建插件，构建走 Vite 直打（见根 package.json build:tdesign） */
export default defineConfig(async () => {
  return {
    application: {
      archiver: false,
      devtools: false,
      html: false,
      injectMetadata: false,
      license: false,
      pwa: false,
    },
    vite: {
      build: {
        target: 'es2020',
      },
      optimizeDeps: {
        include: [
          'dayjs',
          'echarts',
          'pinia',
          'tdesign-vue-next',
          'vue',
          'vue-router',
        ],
      },
      server: {
        proxy: {
          '/api': {
            changeOrigin: true,
            // 后端 FastAPI 服务地址
            target: 'http://localhost:8001',
            ws: true,
          },
        },
      },
    },
  };
});
