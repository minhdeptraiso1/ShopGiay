<script setup lang="ts">
import { onBeforeUnmount, onMounted, watch } from "vue";

import BaseButton from "@/components/base/BaseButton.vue";

interface Props {
  modelValue: boolean;
  title?: string;
  message: string;
  variant?: "error" | "warning" | "info" | "success";
  mode?: "alert" | "confirm";
  actionText?: string;
  cancelText?: string;
  loading?: boolean;
}

const props = withDefaults(defineProps<Props>(), {
  title: "",
  variant: "error",
  mode: "alert",
  actionText: "",
  cancelText: "Hủy bỏ",
  loading: false,
});

const emit = defineEmits<{
  "update:modelValue": [value: boolean];
  close: [];
  confirm: [];
  cancel: [];
}>();

function close() {
  if (props.loading) return;
  emit("update:modelValue", false);
  emit("close");
}

function handleCancel() {
  if (props.loading) return;
  emit("cancel");
  close();
}

function handleConfirm() {
  if (props.loading) return;
  emit("confirm");
  if (props.mode === "alert") {
    close();
  }
}

function handleKeydown(e: KeyboardEvent) {
  if (e.key === "Escape" && props.modelValue && !props.loading) {
    handleCancel();
  }
}

onMounted(() => {
  window.addEventListener("keydown", handleKeydown);
});

onBeforeUnmount(() => {
  window.removeEventListener("keydown", handleKeydown);
});

watch(
  () => props.modelValue,
  (isOpen) => {
    if (typeof document !== "undefined") {
      document.body.style.overflow = isOpen ? "hidden" : "";
    }
  },
);
</script>

<template>
  <Teleport to="body">
    <Transition name="popup-fade">
      <div
        v-if="modelValue"
        class="fixed inset-0 z-50 flex items-center justify-center p-4 sm:p-6"
        role="dialog"
        aria-modal="true"
        aria-labelledby="popup-title"
      >
        <!-- Backdrop -->
        <div
          class="fixed inset-0 bg-black/80 backdrop-blur-md transition-opacity"
          aria-hidden="true"
          @click="close"
        />

        <!-- Modal Dialog Box -->
        <div
          class="relative z-10 w-full max-w-sm sm:max-w-md overflow-hidden rounded-3xl border border-white/15 bg-[#12151e] p-6 sm:p-8 text-center text-white shadow-[0_25px_70px_rgba(0,0,0,0.95)]"
        >
          <!-- Close Button -->
          <button
            type="button"
            class="absolute top-4 right-4 flex h-8 w-8 items-center justify-center rounded-full text-slate-400 hover:bg-white/10 hover:text-white transition-colors cursor-pointer"
            aria-label="Đóng hộp thoại"
            :disabled="loading"
            @click="handleCancel"
          >
            <svg class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2.5">
              <path stroke-linecap="round" stroke-linejoin="round" d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>

          <!-- Status Icon -->
          <div class="mx-auto mb-4 flex h-14 w-14 items-center justify-center rounded-2xl">
            <div
              v-if="variant === 'error'"
              class="flex h-14 w-14 items-center justify-center rounded-2xl border border-rose-500/30 bg-rose-500/10 text-rose-400 shadow-[0_0_25px_rgba(244,63,94,0.2)]"
            >
              <svg class="h-7 w-7" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
                <path stroke-linecap="round" stroke-linejoin="round" d="M12 9v3.75m9-.75a9 9 0 11-18 0 9 9 0 0118 0zm-9 3.75h.008v.008H12v-.008z" />
              </svg>
            </div>
            <div
              v-else-if="variant === 'warning'"
              class="flex h-14 w-14 items-center justify-center rounded-2xl border border-amber-500/30 bg-amber-500/10 text-amber-400 shadow-[0_0_25px_rgba(245,158,11,0.2)]"
            >
              <svg class="h-7 w-7" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
                <path stroke-linecap="round" stroke-linejoin="round" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
              </svg>
            </div>
            <div
              v-else
              class="flex h-14 w-14 items-center justify-center rounded-2xl border border-emerald-500/30 bg-emerald-500/10 text-emerald-400 shadow-[0_0_25px_rgba(16,185,129,0.2)]"
            >
              <svg class="h-7 w-7" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
                <path stroke-linecap="round" stroke-linejoin="round" d="M9 12.75L11.25 15 15 9.75M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
            </div>
          </div>

          <!-- Title -->
          <h2 id="popup-title" class="text-xl font-black uppercase tracking-tight text-white">
            {{ title || (mode === 'confirm' ? 'Xác nhận hành động' : variant === 'error' ? 'Thông Báo Lỗi' : 'Thông Báo') }}
          </h2>

          <!-- Message -->
          <p class="mt-2.5 text-sm sm:text-base leading-relaxed text-slate-300">
            {{ message }}
          </p>

          <!-- Action Buttons -->
          <!-- Alert Mode (Single Action Button) -->
          <div v-if="mode === 'alert'" class="mt-6 pt-2">
            <BaseButton
              type="button"
              block
              class="min-h-12 text-sm font-black uppercase tracking-wider"
              :loading="loading"
              @click="handleConfirm"
            >
              {{ actionText || 'Đã hiểu' }}
            </BaseButton>
          </div>

          <!-- Confirm Mode (Cancel + Confirm Buttons) -->
          <div v-else class="mt-6 pt-2 grid grid-cols-2 gap-3">
            <BaseButton
              type="button"
              variant="ghost"
              class="min-h-12 rounded-xl border border-white/20 bg-white/5 text-slate-200 hover:bg-white/10 text-sm font-bold uppercase tracking-wider"
              :disabled="loading"
              @click="handleCancel"
            >
              {{ cancelText || 'Hủy bỏ' }}
            </BaseButton>
            <BaseButton
              type="button"
              :class="[
                'min-h-12 rounded-xl text-sm font-black uppercase tracking-wider',
                variant === 'error'
                  ? 'bg-rose-600 hover:bg-rose-500 text-white border-0 shadow-[0_0_20px_rgba(244,63,94,0.35)]'
                  : ''
              ]"
              :loading="loading"
              @click="handleConfirm"
            >
              {{ actionText || 'Xác nhận' }}
            </BaseButton>
          </div>
        </div>
      </div>
    </Transition>
  </Teleport>
</template>

<style scoped>
.popup-fade-enter-active,
.popup-fade-leave-active {
  transition: opacity 0.2s ease;
}

.popup-fade-enter-active > div:last-child,
.popup-fade-leave-active > div:last-child {
  transition: transform 0.2s cubic-bezier(0.16, 1, 0.3, 1), opacity 0.2s ease;
}

.popup-fade-enter-from,
.popup-fade-leave-to {
  opacity: 0;
}

.popup-fade-enter-from > div:last-child {
  transform: scale(0.95) translateY(10px);
  opacity: 0;
}

.popup-fade-leave-to > div:last-child {
  transform: scale(0.98) translateY(4px);
  opacity: 0;
}
</style>
