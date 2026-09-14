<script setup lang="ts">
import { storeToRefs } from "pinia";

import { useToastStore } from "@/app/stores/toast";
import BaseButton from "@/components/base/BaseButton.vue";

const toast = useToastStore();
const { message, variant } = storeToRefs(toast);
const styles = {
  success: "border-green-200 bg-green-50 text-green-900",
  error: "border-red-200 bg-red-50 text-red-900",
  info: "border-blue-200 bg-blue-50 text-blue-900",
};
</script>

<template>
  <Transition name="toast">
    <div
      v-if="message"
      class="fixed right-4 bottom-4 z-50 flex max-w-[calc(100vw-2rem)] items-center gap-3 rounded-[var(--radius-md)] border px-4 py-3 shadow-lg sm:max-w-md"
      :class="styles[variant]"
      role="status"
      aria-live="polite"
    >
      <p class="text-sm font-medium">{{ message }}</p>
      <BaseButton size="sm" variant="ghost" aria-label="Đóng thông báo" @click="toast.dismiss">
        Đóng
      </BaseButton>
    </div>
  </Transition>
</template>

<style scoped>
.toast-enter-active,
.toast-leave-active {
  transition:
    opacity 180ms ease,
    transform 180ms ease;
}
.toast-enter-from,
.toast-leave-to {
  opacity: 0;
  transform: translateY(8px);
}
</style>
