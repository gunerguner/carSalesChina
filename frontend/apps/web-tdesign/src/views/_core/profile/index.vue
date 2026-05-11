<script setup lang="ts">
import { ref } from 'vue';

import { Profile } from '@vben/common-ui';
import { useUserStore } from '@vben/stores';

import ProfileSecuritySetting from './security-setting.vue';

const userStore = useUserStore();

const tabsValue = ref<string>('security');

const tabs = ref([
  {
    label: '安全设置',
    value: 'security',
  },
]);
</script>

<template>
  <Profile
    v-model:model-value="tabsValue"
    title="个人中心"
    :user-info="userStore.userInfo"
    :tabs="tabs"
  >
    <template #content>
      <ProfileSecuritySetting v-if="tabsValue === 'security'" />
    </template>
  </Profile>
</template>