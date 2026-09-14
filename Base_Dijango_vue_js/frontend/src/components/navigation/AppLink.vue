<script setup lang="ts">
import { RouterLink, type RouteLocationRaw } from "vue-router";

withDefaults(defineProps<{ to: RouteLocationRaw; variant?: "default" | "nav" }>(), {
  variant: "default",
});
</script>

<template>
  <RouterLink
    :to="to"
    class="cursor-pointer rounded-md font-semibold text-[var(--color-primary)] underline-offset-4 transition-colors hover:text-[var(--color-primary-hover)] hover:underline"
  >
    <slot />
  </RouterLink>
</template>
