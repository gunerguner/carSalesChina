<script setup lang="ts">
import { BasicLayout } from '@vben/layouts';

import AdminRefreshButton from '#/components/AdminRefreshButton.vue';
</script>

<template>
  <BasicLayout>
    <template #header-right-40>
      <AdminRefreshButton />
    </template>
  </BasicLayout>
</template>
