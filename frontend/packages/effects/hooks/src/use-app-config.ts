import type {
  ApplicationConfig,
  VbenAdminProAppConfigRaw,
} from '@vben/types/global';

/**
 * 由 vite-inject-app-config 注入的全局配置
 */
export function useAppConfig(
  env: Record<string, any>,
  isProduction: boolean,
): ApplicationConfig {
  const envVars = env as VbenAdminProAppConfigRaw;
  // 生产：优先 _app.config.js；Docker 构建若未注入则回退到打包进 bundle 的 import.meta.env
  const runtime = isProduction
    ? {
        ...envVars,
        ...(typeof window !== 'undefined'
          ? window._VBEN_ADMIN_PRO_APP_CONF_
          : undefined),
      }
    : envVars;

  const {
    VITE_GLOB_API_URL = '/api',
    VITE_GLOB_AUTH_DINGDING_CORP_ID,
    VITE_GLOB_AUTH_DINGDING_CLIENT_ID,
  } = runtime;

  const applicationConfig: ApplicationConfig = {
    apiURL: VITE_GLOB_API_URL,
    auth: {},
  };
  if (VITE_GLOB_AUTH_DINGDING_CORP_ID && VITE_GLOB_AUTH_DINGDING_CLIENT_ID) {
    applicationConfig.auth.dingding = {
      clientId: VITE_GLOB_AUTH_DINGDING_CLIENT_ID,
      corpId: VITE_GLOB_AUTH_DINGDING_CORP_ID,
    };
  }

  return applicationConfig;
}
