import { defineStore } from "pinia";
import { ref } from "vue";

export type ToastVariant = "success" | "error" | "info";

export const useToastStore = defineStore("toast", () => {
  const message = ref("");
  const variant = ref<ToastVariant>("info");
  let timer: ReturnType<typeof setTimeout> | undefined;

  function show(nextMessage: string, nextVariant: ToastVariant = "info") {
    if (timer) clearTimeout(timer);
    message.value = nextMessage;
    variant.value = nextVariant;
    timer = setTimeout(() => {
      message.value = "";
      timer = undefined;
    }, 4500);
  }

  function dismiss() {
    if (timer) clearTimeout(timer);
    message.value = "";
    timer = undefined;
  }

  return { message, variant, show, dismiss };
});
