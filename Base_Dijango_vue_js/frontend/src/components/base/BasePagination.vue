<script setup lang="ts">
import { computed } from "vue";

import BaseButton from "./BaseButton.vue";

const props = withDefaults(
  defineProps<{ count: number; page: number; pageSize?: number; disabled?: boolean }>(),
  { pageSize: 20, disabled: false },
);

const emit = defineEmits<{ "update:page": [page: number] }>();
const totalPages = computed(() => Math.max(1, Math.ceil(props.count / props.pageSize)));
</script>

<template>
  <nav class="flex flex-wrap items-center justify-between gap-3" aria-label="Phân trang">
    <p class="text-xs text-slate-500">
      Trang {{ page }}/{{ totalPages }} · {{ count.toLocaleString("vi-VN") }} kết quả
    </p>
    <div class="flex gap-2">
      <BaseButton
        size="sm"
        variant="secondary"
        :disabled="disabled || page <= 1"
        @click="emit('update:page', page - 1)"
      >
        Trang trước
      </BaseButton>
      <BaseButton
        size="sm"
        variant="secondary"
        :disabled="disabled || page >= totalPages"
        @click="emit('update:page', page + 1)"
      >
        Trang sau
      </BaseButton>
    </div>
  </nav>
</template>
