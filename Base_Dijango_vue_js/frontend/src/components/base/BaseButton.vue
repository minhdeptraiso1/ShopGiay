<script setup lang="ts">
import BaseSpinner from "./BaseSpinner.vue";

interface Props {
  type?: "button" | "submit" | "reset";
  variant?: "primary" | "secondary" | "danger" | "ghost";
  size?: "sm" | "md";
  loading?: boolean;
  disabled?: boolean;
  block?: boolean;
}

const props = withDefaults(defineProps<Props>(), {
  type: "button",
  variant: "primary",
  size: "md",
  loading: false,
  disabled: false,
  block: false,
});

const variants = {
  primary: "bg-[var(--color-primary)] text-white hover:bg-[var(--color-primary-hover)]",
  secondary:
    "border border-[var(--color-border)] bg-white text-[var(--color-primary)] hover:bg-[var(--color-primary-soft)]",
  danger: "bg-[var(--color-error)] text-white hover:brightness-90",
  ghost: "bg-transparent text-[var(--color-primary)] hover:bg-[var(--color-primary-soft)]",
};
</script>

<template>
  <button
    :type="props.type"
    :disabled="props.disabled || props.loading"
    :aria-busy="props.loading"
    class="inline-flex cursor-pointer items-center justify-center gap-2 rounded-[var(--radius-sm)] font-semibold shadow-sm transition-colors disabled:cursor-not-allowed disabled:opacity-55"
    :class="[
      variants[props.variant],
      props.size === 'sm' ? 'min-h-10 px-3 text-sm' : 'min-h-11 px-4 text-sm',
      props.block && 'w-full',
    ]"
  >
    <BaseSpinner v-if="props.loading" />
    <slot />
  </button>
</template>
