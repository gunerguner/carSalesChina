<script setup lang="ts">
import { BasicLayout } from '@vben/layouts';

import AdminRefreshButton from '#/components/AdminRefreshButton.vue';
import AppFooter from '#/components/Footer/AppFooter.vue';
</script>

<template>
  <BasicLayout>
    <template #header-right-40>
      <AdminRefreshButton />
    </template>
    <template #footer>
      <AppFooter />
    </template>
  </BasicLayout>
</template>
