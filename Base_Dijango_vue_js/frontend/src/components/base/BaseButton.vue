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
  primary:
    "bg-[var(--color-primary-btn-bg,#10b981)] text-[var(--color-primary-btn-text,#000000)] hover:brightness-110 active:scale-[0.99] font-black tracking-wider uppercase shadow-md shadow-emerald-500/20",
  secondary:
    "border border-[var(--color-border)] bg-[var(--color-surface)] text-[var(--color-text)] hover:bg-[var(--color-primary-soft)]",
  danger: "bg-[var(--color-error)] text-white hover:brightness-90",
  ghost: "bg-transparent text-[var(--color-text-muted,#94a3b8)] hover:text-white hover:bg-white/5",
};
</script>

<template>
  <button
    :type="props.type"
    :disabled="props.disabled || props.loading"
    :aria-busy="props.loading"
    class="inline-flex cursor-pointer items-center justify-center gap-2 rounded-xl font-bold shadow-sm transition-all duration-200 disabled:cursor-not-allowed disabled:opacity-50"
    :class="[
      variants[props.variant],
      props.size === 'sm' ? 'min-h-10 px-3.5 text-xs' : 'min-h-12 px-5 text-sm',
      props.block && 'w-full',
    ]"
  >
    <BaseSpinner v-if="props.loading" />
    <slot />
  </button>
</template>
