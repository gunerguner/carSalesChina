<script setup lang="ts">
import { computed } from 'vue';

import { IconifyIcon } from '@vben/icons';

defineOptions({
  name: 'AppFooter',
});

const VBEN_LOGO_SRC =
  'https://unpkg.com/@vbenjs/static-source@0.1.7/source/logo-v1.webp';

const START_YEAR = 2020;
const CURRENT_YEAR = new Date().getFullYear();

const copyrightText = computed(
  () =>
    `${START_YEAR}${CURRENT_YEAR > START_YEAR ? `-${CURRENT_YEAR}` : ''} 溯宁`,
);

const ICON_LINKS = [
  {
    key: 'fastapi',
    title: 'FastAPI',
    href: 'https://fastapi.tiangolo.com/',
    icon: 'simple-icons:fastapi',
  },
  {
    key: 'vben',
    title: 'Vben Admin',
    href: 'https://doc.vben.pro/',
    image: VBEN_LOGO_SRC,
  },
  {
    key: 'github',
    title: 'GitHub',
    href: 'https://github.com/gunerguner/carSalesChina',
    icon: 'mdi:github',
  },
] as const;

const ICP_LINK = {
  title: '沪ICP备2020026170号',
  href: 'https://beian.miit.gov.cn/',
};
</script>

<template>
  <div class="app-footer">
    <div class="app-footer__links">
      <a
        v-for="link in ICON_LINKS"
        :key="link.key"
        :href="link.href"
        :title="link.title"
        class="app-footer__icon-link"
        rel="noopener noreferrer"
        target="_blank"
      >
        <img
          v-if="'image' in link"
          :alt="link.title"
          :src="link.image"
          class="app-footer__icon-img"
        />
        <IconifyIcon v-else :icon="link.icon" class="app-footer__icon" />
      </a>
      <a
        :href="ICP_LINK.href"
        class="app-footer__link"
        rel="noopener noreferrer"
        target="_blank"
      >
        {{ ICP_LINK.title }}
      </a>
    </div>
    <div class="app-footer__copyright">Copyright © {{ copyrightText }}</div>
  </div>
</template>

<style scoped>
.app-footer {
  display: flex;
  flex-direction: column;
  gap: 4px;
  align-items: center;
  justify-content: center;
  width: 100%;
  padding: 0 8px;
  line-height: 1.5;
  text-align: center;
}

.app-footer__links {
  display: flex;
  flex-wrap: wrap;
  gap: 14px;
  align-items: center;
  justify-content: center;
}

.app-footer__icon-link {
  display: flex;
  align-items: center;
  color: hsl(var(--muted-foreground));
  text-decoration: none;
  transition: color 0.2s;
}

.app-footer__icon-link:hover {
  color: hsl(var(--primary));
}

.app-footer__icon {
  width: 16px;
  height: 16px;
}

.app-footer__icon-img {
  width: 16px;
  height: 16px;
  object-fit: contain;
}

.app-footer__link {
  color: hsl(var(--muted-foreground));
  text-decoration: none;
  transition: color 0.2s;
}

.app-footer__link:hover {
  color: hsl(var(--primary));
}

.app-footer__copyright {
  color: hsl(var(--muted-foreground));
}
</style>
