<script setup lang="ts">
import { nextTick, onBeforeUnmount, ref, watch } from "vue";

const props = withDefaults(
  defineProps<{ modelValue: boolean; title: string; description?: string; busy?: boolean }>(),
  { description: "", busy: false },
);
const emit = defineEmits<{ "update:modelValue": [value: boolean] }>();
const panel = ref<HTMLElement | null>(null);
let previousFocus: HTMLElement | null = null;

function close(): void {
  if (!props.busy) emit("update:modelValue", false);
}

function handleKeydown(event: KeyboardEvent): void {
  if (!props.modelValue) return;
  if (event.key === "Escape") close();
  if (event.key !== "Tab" || !panel.value) return;
  const focusable = [
    ...panel.value.querySelectorAll<HTMLElement>(
      'button:not([disabled]), input:not([disabled]), select:not([disabled]), textarea:not([disabled]), [href], [tabindex]:not([tabindex="-1"])',
    ),
  ];
  if (!focusable.length) return;
  const first = focusable[0];
  const last = focusable[focusable.length - 1];
  if (event.shiftKey && globalThis.document.activeElement === first) {
    event.preventDefault();
    last?.focus();
  } else if (!event.shiftKey && globalThis.document.activeElement === last) {
    event.preventDefault();
    first?.focus();
  }
}

watch(
  () => props.modelValue,
  async (open) => {
    if (open) {
      previousFocus = globalThis.document.activeElement as HTMLElement | null;
      globalThis.document.body.style.overflow = "hidden";
      await nextTick();
      panel.value?.querySelector<HTMLElement>("input, button, select, textarea")?.focus();
    } else {
      globalThis.document.body.style.overflow = "";
      previousFocus?.focus();
    }
  },
);

globalThis.addEventListener("keydown", handleKeydown);
onBeforeUnmount(() => {
  globalThis.removeEventListener("keydown", handleKeydown);
  globalThis.document.body.style.overflow = "";
});
</script>

<template>
  <Teleport to="body">
    <div v-if="modelValue" class="fixed inset-0 z-[70] grid place-items-center p-4">
      <button
        class="absolute inset-0 bg-black/75 backdrop-blur-sm"
        aria-label="Đóng hộp thoại"
        @click="close"
      />
      <section
        ref="panel"
        role="dialog"
        aria-modal="true"
        aria-labelledby="dialog-title"
        aria-describedby="dialog-description"
        class="relative z-10 max-h-[90vh] w-full max-w-2xl overflow-y-auto rounded-3xl border border-white/15 bg-[#12151e] p-6 text-white shadow-2xl"
      >
        <button
          type="button"
          class="absolute top-4 right-4 rounded-lg px-3 py-2 text-slate-400 hover:bg-white/10 hover:text-white"
          :disabled="busy"
          aria-label="Đóng"
          @click="close"
        >
          ✕
        </button>
        <header class="pr-12">
          <h2 id="dialog-title" class="text-2xl font-black">{{ title }}</h2>
          <p v-if="description" id="dialog-description" class="mt-2 text-sm text-slate-400">
            {{ description }}
          </p>
        </header>
        <div class="mt-6"><slot /></div>
      </section>
    </div>
  </Teleport>
</template>
