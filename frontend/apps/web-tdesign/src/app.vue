<script lang="ts" setup>
import type { GlobalConfigProvider } from 'tdesign-vue-next';

import { computed, watch } from 'vue';

import { usePreferences } from '@vben/preferences';

import { merge } from 'es-toolkit/compat';
import { ConfigProvider } from 'tdesign-vue-next';
import enConfig from 'tdesign-vue-next/es/locale/en_US';
import zhConfig from 'tdesign-vue-next/es/locale/zh_CN';

defineOptions({ name: 'App' });
const { isDark, locale } = usePreferences();

watch(
  () => isDark.value,
  (dark) => {
    document.documentElement.setAttribute('theme-mode', dark ? 'dark' : '');
  },
  { immediate: true },
);

const customConfig: GlobalConfigProvider = {
  calendar: {},
  table: {},
  pagination: {},
};
const localeConfig = computed(() =>
  locale.value === 'en-US' ? enConfig : zhConfig,
);
const globalConfig = computed<GlobalConfigProvider>(() =>
  merge({}, localeConfig.value, customConfig),
);
</script>

<template>
  <ConfigProvider :global-config="globalConfig" class="app">
    <RouterView />
  </ConfigProvider>
</template>
