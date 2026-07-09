<script setup lang="ts">
import type { SupportedLanguagesType } from '@vben/locales';

import { computed } from 'vue';

import { Languages } from '@vben/icons';
import { $t, loadLocaleMessages } from '@vben/locales';
import { preferences, updatePreferences } from '@vben/preferences';

import { VbenIconButton } from '@vben-core/shadcn-ui';

defineOptions({
  name: 'LanguageToggle',
});

const localeToggleHint = computed(() =>
  preferences.app.locale === 'zh-CN'
    ? $t('preferences.widget.switchToEn')
    : $t('preferences.widget.switchToZh'),
);

async function toggleLocale() {
  const locale: SupportedLanguagesType =
    preferences.app.locale === 'zh-CN' ? 'en-US' : 'zh-CN';
  updatePreferences({
    app: {
      locale,
    },
  });
  await loadLocaleMessages(locale);
}
</script>

<template>
  <div>
    <VbenIconButton
      class="hover:animate-[shrink_0.3s_ease-in-out]"
      :tooltip="localeToggleHint"
      @click="toggleLocale"
    >
      <Languages class="size-4 text-foreground" />
    </VbenIconButton>
  </div>
</template>
