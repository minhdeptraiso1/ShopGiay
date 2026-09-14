<script setup lang="ts">
interface Props {
  variant?: "info" | "success" | "warning" | "error";
  title?: string;
}

const props = withDefaults(defineProps<Props>(), { variant: "info", title: "" });
const styles = {
  info: "border-blue-200 bg-blue-50 text-blue-900",
  success: "border-green-200 bg-[var(--color-success-soft)] text-green-900",
  warning: "border-yellow-200 bg-[var(--color-warning-soft)] text-yellow-900",
  error: "border-red-200 bg-[var(--color-error-soft)] text-red-900",
};
</script>

<template>
  <div
    class="rounded-[var(--radius-sm)] border p-3 text-sm"
    :class="styles[props.variant]"
    :role="props.variant === 'error' ? 'alert' : 'status'"
  >
    <p v-if="props.title" class="font-semibold">{{ props.title }}</p>
    <div :class="props.title && 'mt-1'"><slot /></div>
  </div>
</template>
