<template>
  <div class="chart-card page-card">
    <div class="card-header">
      <h3>{{ title }}</h3>
      <slot name="actions" />
    </div>
    <div class="card-body">
      <slot />
    </div>
  </div>
</template>

<script setup lang="ts">
defineProps<{ title: string }>();
</script>

<style scoped>
.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
}
.card-header h3 {
  margin: 0;
  font-size: 16px;
}
</style>