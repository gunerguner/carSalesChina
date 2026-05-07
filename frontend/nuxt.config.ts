export default defineNuxtConfig({
  ssr: false,
  modules: ["@unocss/nuxt"],
  css: ["element-plus/dist/index.css", "@/assets/css/main.css"],
  devtools: { enabled: false },
  runtimeConfig: {
    public: {
      apiBase: "http://localhost:8001",
    },
  },
  vite: {
    server: {
      proxy: {
        "/api": {
          target: "http://localhost:8001",
          changeOrigin: true,
        },
      },
    },
  },
  compatibilityDate: "2025-05-07",
});