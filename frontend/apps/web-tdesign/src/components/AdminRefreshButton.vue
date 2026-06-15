<script setup lang="ts">
import { ref } from 'vue';

import { VbenIconButton } from '@vben/common-ui';
import { RotateCw } from '@vben/icons';

import { Dialog, Input, MessagePlugin as message } from 'tdesign-vue-next';

import { useAdminDataRefresh } from '#/composables/useAdminDataRefresh';
import { $t } from '#/locales';

const CONFIRM_CODE = import.meta.env.VITE_ADMIN_REFRESH_CONFIRM_CODE ?? '';

const { refreshAdminData, refreshing } = useAdminDataRefresh();
const dialogVisible = ref(false);
const inputCode = ref('');

function openConfirmDialog() {
  if (refreshing.value) return;
  inputCode.value = '';
  dialogVisible.value = true;
}

function handleClose() {
  dialogVisible.value = false;
  inputCode.value = '';
}

function handleConfirm() {
  if (!CONFIRM_CODE) {
    message.error($t('pages.admin.refreshConfirmNotConfigured'));
    return;
  }
  if (inputCode.value !== CONFIRM_CODE) {
    message.error($t('pages.admin.refreshConfirmCodeInvalid'));
    return;
  }
  handleClose();
  void refreshAdminData();
}
</script>

<template>
  <VbenIconButton
    class="my-0 mr-1 rounded-md"
    :disabled="refreshing"
    @click="openConfirmDialog"
  >
    <RotateCw class="size-4" :class="{ 'animate-spin': refreshing }" />
  </VbenIconButton>

  <Dialog
    v-model:visible="dialogVisible"
    :header="$t('pages.admin.refreshConfirmTitle')"
    :confirm-btn="{
      content: $t('pages.admin.refreshConfirmSubmit'),
      theme: 'danger',
    }"
    :cancel-btn="$t('pages.admin.refreshConfirmCancel')"
    @confirm="handleConfirm"
    @close="handleClose"
  >
    <p class="mb-4 text-sm text-muted-foreground">
      {{ $t('pages.admin.refreshConfirmContent') }}
    </p>
    <Input
      v-model="inputCode"
      :placeholder="$t('pages.admin.refreshConfirmPlaceholder')"
      clearable
      @enter="handleConfirm"
    />
  </Dialog>
</template>
