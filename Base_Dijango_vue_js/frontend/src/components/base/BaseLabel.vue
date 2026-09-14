<script setup lang="ts">
withDefaults(defineProps<{ forId: string; required?: boolean }>(), { required: false });
</script>

<template>
  <label :for="forId" class="block text-sm font-semibold text-[var(--color-text)]">
    <slot />
    <span v-if="required" class="ml-1 text-[var(--color-error)]" aria-hidden="true">*</span>
    <span v-if="required" class="sr-only">(bắt buộc)</span>
  </label>
</template>
