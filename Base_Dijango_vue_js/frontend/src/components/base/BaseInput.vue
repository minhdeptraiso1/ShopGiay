<script setup lang="ts">
import { computed, ref, useAttrs } from "vue";

defineOptions({ inheritAttrs: false });

interface Props {
  modelValue: string;
  id: string;
  name: string;
  type?: "text" | "email" | "password" | "number" | "datetime-local" | "url";
  autocomplete?: string;
  placeholder?: string;
  disabled?: boolean;
  readonly?: boolean;
  required?: boolean;
  invalid?: boolean;
}

const props = withDefaults(defineProps<Props>(), {
  type: "text",
  autocomplete: "off",
  placeholder: "",
  disabled: false,
  readonly: false,
  required: false,
  invalid: false,
});
const emit = defineEmits<{ "update:modelValue": [value: string]; blur: [event: FocusEvent] }>();
const attrs = useAttrs();
const passwordVisible = ref(false);
const actualType = computed(() =>
  props.type === "password" && passwordVisible.value ? "text" : props.type,
);
</script>

<template>
  <div class="relative">
    <input
      v-bind="attrs"
      :id="props.id"
      :name="props.name"
      :value="props.modelValue"
      :type="actualType"
      :autocomplete="props.autocomplete"
      :placeholder="props.placeholder"
      :disabled="props.disabled"
      :readonly="props.readonly"
      :required="props.required"
      :aria-invalid="props.invalid || undefined"
      class="min-h-12 w-full rounded-xl border bg-[var(--color-input-bg,#ffffff)] px-3.5 text-base text-[var(--color-text)] shadow-sm transition-all placeholder:text-slate-500 focus:outline-none focus:border-[var(--color-focus,#10b981)] focus:ring-2 focus:ring-[var(--color-focus,#10b981)]/20 disabled:cursor-not-allowed disabled:bg-slate-800/40 disabled:text-slate-500 sm:text-sm"
      :class="[
        props.invalid
          ? 'border-[var(--color-error)] focus:border-[var(--color-error)] focus:ring-[var(--color-error)]/20'
          : 'border-[var(--color-border)] hover:border-emerald-500/50',
        props.type === 'password' && 'pr-16',
      ]"
      @input="emit('update:modelValue', ($event.target as HTMLInputElement).value)"
      @blur="emit('blur', $event)"
    />
    <button
      v-if="props.type === 'password'"
      type="button"
      class="absolute inset-y-0 right-1.5 my-auto flex h-9 min-w-12 items-center justify-center cursor-pointer rounded-lg px-2 text-xs font-bold uppercase tracking-wider text-[var(--color-primary)] hover:bg-[var(--color-primary-soft)] transition-colors"
      :aria-label="passwordVisible ? 'Ẩn mật khẩu' : 'Hiện mật khẩu'"
      @click="passwordVisible = !passwordVisible"
    >
      {{ passwordVisible ? "Ẩn" : "Hiện" }}
    </button>
  </div>
</template>
