import { createApp, watchEffect } from 'vue';

import { preferences } from '@vben/preferences';
import { initStores } from '@vben/stores';
import '@vben/styles';

import { useTitle } from '@vueuse/core';

import { $t, setupI18n } from '#/locales';

import App from './app.vue';
import { router } from './router';

import 'tdesign-vue-next/es/style/index.css';

async function bootstrap(namespace: string) {
  const app = createApp(App);

  await setupI18n(app);

  await initStores(app, { namespace });

  app.use(router);

  const title = useTitle();
  watchEffect(() => {
    if (preferences.app.dynamicTitle) {
      const routeTitle = router.currentRoute.value.meta?.title;
      title.value =
        (routeTitle ? `${$t(routeTitle)} - ` : '') + preferences.app.name;
      return;
    }
    title.value = preferences.app.name;
  });

  app.mount('#app');
}

export { bootstrap };
