<script setup lang="ts">
import { storeToRefs } from "pinia";

import { useToastStore } from "@/app/stores/toast";
import BaseButton from "@/components/base/BaseButton.vue";

const toast = useToastStore();
const { message, variant } = storeToRefs(toast);
const styles = {
  success: "border-emerald-500/30 bg-[#12151e]/95 text-emerald-300 shadow-[0_10px_30px_rgba(16,185,129,0.2)]",
  error: "border-rose-500/30 bg-[#12151e]/95 text-rose-300 shadow-[0_10px_30px_rgba(244,63,94,0.2)]",
  info: "border-sky-500/30 bg-[#12151e]/95 text-sky-300 shadow-[0_10px_30px_rgba(56,189,248,0.2)]",
};
</script>

<template>
  <Transition name="toast">
    <div
      v-if="message"
      class="fixed top-6 right-6 z-50 flex max-w-[calc(100vw-2rem)] items-center gap-3 rounded-2xl border px-5 py-3.5 shadow-2xl backdrop-blur-md sm:max-w-md"
      :class="styles[variant]"
      role="status"
      aria-live="polite"
    >
      <p class="text-sm font-semibold">{{ message }}</p>
      <BaseButton size="sm" variant="ghost" aria-label="Đóng thông báo" class="text-xs uppercase font-bold" @click="toast.dismiss">
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
