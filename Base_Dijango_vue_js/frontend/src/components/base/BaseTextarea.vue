<script setup lang="ts">
defineOptions({ inheritAttrs: false });

interface Props {
  modelValue: string;
  id: string;
  name: string;
  placeholder?: string;
  rows?: number;
  disabled?: boolean;
  required?: boolean;
  invalid?: boolean;
}

const props = withDefaults(defineProps<Props>(), {
  placeholder: "",
  rows: 4,
  disabled: false,
  required: false,
  invalid: false,
});
const emit = defineEmits<{ "update:modelValue": [value: string] }>();
</script>

<template>
  <textarea
    v-bind="$attrs"
    :id="props.id"
    :name="props.name"
    :value="props.modelValue"
    :placeholder="props.placeholder"
    :rows="props.rows"
    :disabled="props.disabled"
    :required="props.required"
    :aria-invalid="props.invalid || undefined"
    class="w-full resize-y rounded-xl border border-[var(--color-border)] bg-[var(--color-input-bg,#ffffff)] px-3.5 py-3 text-sm text-[var(--color-text)] shadow-sm transition-all placeholder:text-slate-500 focus:border-[var(--color-focus,#10b981)] focus:ring-2 focus:ring-[var(--color-focus,#10b981)]/20 focus:outline-none disabled:cursor-not-allowed disabled:opacity-60"
    @input="emit('update:modelValue', ($event.target as HTMLTextAreaElement).value)"
  />
</template>
