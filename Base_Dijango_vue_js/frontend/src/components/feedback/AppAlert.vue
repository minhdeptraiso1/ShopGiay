<script setup lang="ts">
interface Props {
  variant?: "info" | "success" | "warning" | "error";
  title?: string;
}

const props = withDefaults(defineProps<Props>(), { variant: "info", title: "" });
const styles = {
  info: "border-sky-500/30 bg-sky-500/10 text-sky-300",
  success: "border-emerald-500/30 bg-emerald-500/10 text-emerald-300",
  warning: "border-amber-500/30 bg-amber-500/10 text-amber-300",
  error: "border-rose-500/30 bg-rose-500/10 text-rose-300",
};
</script>

<template>
  <div
    class="rounded-xl border p-3.5 text-sm backdrop-blur-sm"
    :class="styles[props.variant]"
    :role="props.variant === 'error' ? 'alert' : 'status'"
  >
    <p v-if="props.title" class="font-bold tracking-wide uppercase text-xs mb-1">{{ props.title }}</p>
    <div><slot /></div>
  </div>
</template>
