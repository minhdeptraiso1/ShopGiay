<script setup lang="ts">
withDefaults(defineProps<{ label?: string; size?: "sm" | "md" }>(), {
  label: "Đang xử lý",
  size: "sm",
});
</script>

<template>
  <span
    class="inline-block animate-spin rounded-full border-2 border-current border-r-transparent"
    :class="size === 'sm' ? 'size-4' : 'size-6'"
    role="status"
  >
    <span class="sr-only">{{ label }}</span>
  </span>
</template>
