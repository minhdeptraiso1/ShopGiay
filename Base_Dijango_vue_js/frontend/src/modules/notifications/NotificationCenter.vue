<script setup lang="ts">
import { onBeforeUnmount, onMounted, ref } from "vue";
import { useRouter } from "vue-router";

import { useNotifications } from "./useNotifications";
import type { NotificationItem } from "./api";

const router = useRouter();
const open = ref(false);
const root = ref<HTMLElement | null>(null);
const { items, unreadCount, connected, load, connect, disconnect, read, readAll } =
  useNotifications();

function handleDocumentClick(event: MouseEvent): void {
  if (root.value && !root.value.contains(event.target as Node)) open.value = false;
}
onMounted(async () => {
  globalThis.document.addEventListener("click", handleDocumentClick);
  try {
    await load();
  } catch {
    // Header remains usable while the API is unavailable; WebSocket reconnects independently.
  }
  await connect();
});
onBeforeUnmount(() => {
  globalThis.document.removeEventListener("click", handleDocumentClick);
  disconnect();
});

async function openItem(item: NotificationItem): Promise<void> {
  await read(item);
  open.value = false;
  if (item.link) await router.push(item.link);
}
</script>

<template>
  <div ref="root" class="relative">
    <button
      type="button"
      class="relative grid h-10 w-10 place-items-center rounded-xl border border-white/10 bg-white/5 text-slate-300 hover:text-white"
      aria-label="Thông báo"
      :aria-expanded="open"
      @click="open = !open"
    >
      <span aria-hidden="true">🔔</span>
      <span
        v-if="unreadCount"
        class="absolute -top-1 -right-1 min-w-5 rounded-full bg-rose-500 px-1 text-center text-[10px] font-black text-white"
        >{{ unreadCount > 99 ? "99+" : unreadCount }}</span
      >
    </button>
    <section
      v-if="open"
      class="absolute top-12 right-0 z-50 w-[min(24rem,calc(100vw-2rem))] overflow-hidden rounded-2xl border border-white/15 bg-[#12151e] shadow-2xl"
      aria-label="Danh sách thông báo"
    >
      <header class="flex items-center justify-between border-b border-white/10 p-4">
        <div>
          <h2 class="font-black text-white">Thông báo</h2>
          <p class="text-[11px] text-slate-500">
            {{ connected ? "Đang cập nhật trực tiếp" : "Đang kết nối lại…" }}
          </p>
        </div>
        <button class="text-xs font-bold text-emerald-400" type="button" @click="readAll">
          Đọc tất cả
        </button>
      </header>
      <div class="max-h-96 overflow-y-auto">
        <button
          v-for="item in items"
          :key="item.id"
          type="button"
          class="block w-full border-b border-white/8 p-4 text-left hover:bg-white/5"
          :class="!item.read_at && 'bg-emerald-500/[0.06]'"
          @click="openItem(item)"
        >
          <span class="flex items-start gap-3">
            <span
              v-if="!item.read_at"
              class="mt-1.5 h-2 w-2 shrink-0 rounded-full bg-emerald-400"
            />
            <span v-else class="w-2 shrink-0" />
            <span>
              <strong class="block text-sm text-white">{{ item.title }}</strong>
              <span class="mt-1 block text-xs leading-5 text-slate-400">{{ item.message }}</span>
              <time class="mt-1 block text-[10px] text-slate-600">{{
                new Date(item.created_at).toLocaleString("vi-VN")
              }}</time>
            </span>
          </span>
        </button>
        <p v-if="!items.length" class="p-8 text-center text-sm text-slate-500">
          Chưa có thông báo.
        </p>
      </div>
    </section>
  </div>
</template>
