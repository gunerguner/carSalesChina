<script setup lang="ts">
import { Card } from 'tdesign-vue-next';

defineProps<{
  title: string;
}>();
</script>

<template>
  <Card :title="title" class="section-card">
    <slot></slot>
  </Card>
</template>
