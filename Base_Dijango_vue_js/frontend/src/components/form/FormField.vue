<script setup lang="ts">
import { computed, useId } from "vue";

import BaseLabel from "@/components/base/BaseLabel.vue";

interface Props {
  label: string;
  name: string;
  help?: string;
  error?: string;
  required?: boolean;
}

const props = withDefaults(defineProps<Props>(), { help: "", error: "", required: false });
const generatedId = useId();
const inputId = computed(() => `${props.name}-${generatedId.replaceAll(":", "")}`);
const helpId = computed(() => `${inputId.value}-help`);
const errorId = computed(() => `${inputId.value}-error`);
const describedBy = computed(() =>
  [props.help ? helpId.value : "", props.error ? errorId.value : ""].filter(Boolean).join(" "),
);
</script>

<template>
  <div class="space-y-1.5">
    <BaseLabel :for-id="inputId" :required="props.required">{{ props.label }}</BaseLabel>
    <slot :id="inputId" :invalid="Boolean(props.error)" :described-by="describedBy || undefined" />
    <p v-if="props.help" :id="helpId" class="text-sm text-[var(--color-text-muted)]">
      {{ props.help }}
    </p>
    <p
      v-if="props.error"
      :id="errorId"
      class="flex items-start gap-1 text-sm font-medium text-[var(--color-error)]"
      role="alert"
    >
      <span aria-hidden="true">—</span>{{ props.error }}
    </p>
  </div>
</template>
