<script setup lang="ts">
import { nextTick, ref } from 'vue';

import { VbenIconButton } from '@vben/common-ui';
import { RotateCw } from '@vben/icons';

import { Dialog, Input, MessagePlugin as message } from 'tdesign-vue-next';

import RefreshProgressModal from '#/components/RefreshProgressModal.vue';
import { useAdminDataRefresh } from '#/composables/useAdminDataRefresh';
import { $t } from '#/locales';

const { refreshAdminData, refreshing } = useAdminDataRefresh();
const dialogVisible = ref(false);
const inputPassword = ref('');
const submitting = ref(false);
const inputRef = ref<null | { focus: () => void }>(null);

function openConfirmDialog() {
  if (refreshing.value) return;
  inputPassword.value = '';
  dialogVisible.value = true;
}

function focusConfirmInput() {
  nextTick(() => {
    inputRef.value?.focus();
  });
}

function handleClose() {
  dialogVisible.value = false;
  inputPassword.value = '';
}

async function handleConfirm() {
  if (submitting.value) return;
  const password = inputPassword.value.trim();
  if (!password) {
    message.error($t('pages.admin.refreshConfirmPlaceholder'));
    return;
  }
  submitting.value = true;
  try {
    const result = await refreshAdminData(password);
    if (!result.accepted) {
      if (result.message) {
        message.error(result.message);
      }
      return;
    }
    handleClose();
  } finally {
    submitting.value = false;
  }
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
      loading: submitting,
    }"
    :cancel-btn="$t('pages.admin.refreshConfirmCancel')"
    @confirm="handleConfirm"
    @close="handleClose"
    @opened="focusConfirmInput"
  >
    <p class="mb-4 text-sm text-muted-foreground">
      {{ $t('pages.admin.refreshConfirmContent') }}
    </p>
    <Input
      ref="inputRef"
      v-model="inputPassword"
      type="password"
      :placeholder="$t('pages.admin.refreshConfirmPlaceholder')"
      clearable
      @enter="handleConfirm"
    />
  </Dialog>

  <RefreshProgressModal />
</template>
