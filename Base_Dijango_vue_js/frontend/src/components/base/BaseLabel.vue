<script setup lang="ts">
withDefaults(defineProps<{ forId: string; required?: boolean }>(), { required: false });
</script>

<template>
  <label :for="forId" class="block text-xs font-bold tracking-wider uppercase text-[var(--color-label-text,var(--color-text))]">
    <slot />
    <span v-if="required" class="ml-1 text-rose-500 font-bold" aria-hidden="true">*</span>
    <span v-if="required" class="sr-only">(bắt buộc)</span>
  </label>
</template>
