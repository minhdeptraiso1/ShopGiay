<script setup lang="ts">
import { computed, ref, useAttrs } from "vue";

defineOptions({ inheritAttrs: false });

interface Props {
  modelValue: string;
  id: string;
  name: string;
  type?: "text" | "email" | "password";
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
      class="min-h-11 w-full rounded-[var(--radius-sm)] border bg-white px-3 text-base text-[var(--color-text)] shadow-sm transition-colors placeholder:text-slate-400 disabled:cursor-not-allowed disabled:bg-slate-100 disabled:text-slate-500 sm:text-sm"
      :class="[
        props.invalid
          ? 'border-[var(--color-error)]'
          : 'border-[var(--color-border)] hover:border-blue-400',
        props.type === 'password' && 'pr-16',
      ]"
      @input="emit('update:modelValue', ($event.target as HTMLInputElement).value)"
      @blur="emit('blur', $event)"
    />
    <button
      v-if="props.type === 'password'"
      type="button"
      class="absolute inset-y-0 right-1 min-w-12 cursor-pointer rounded-md px-2 text-sm font-semibold text-[var(--color-primary)] hover:bg-[var(--color-primary-soft)]"
      :aria-label="passwordVisible ? 'Ẩn mật khẩu' : 'Hiện mật khẩu'"
      @click="passwordVisible = !passwordVisible"
    >
      {{ passwordVisible ? "Ẩn" : "Hiện" }}
    </button>
  </div>
</template>
