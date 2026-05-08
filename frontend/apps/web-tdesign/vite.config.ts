import { defineConfig } from '@vben/vite-config';

export default defineConfig(async () => {
  return {
    application: {},
    vite: {
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
