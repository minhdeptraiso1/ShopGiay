<script setup lang="ts">
import { onMounted, ref } from "vue";

import { useToastStore } from "@/app/stores/toast";
import BaseButton from "@/components/base/BaseButton.vue";
import AppAlert from "@/components/feedback/AppAlert.vue";
import AppLink from "@/components/navigation/AppLink.vue";
import StorefrontLayout from "@/layouts/StorefrontLayout.vue";
import { toAppError } from "@/lib/http/errors";
import { cancelExchange, confirmReplacementReceived, fetchMyExchanges } from "../api";
import { exchangeStatusClass, exchangeStatusLabels } from "../status";
import type { ExchangeRequest, ExchangeStatus } from "../types";

const toast = useToastStore();
const exchanges = ref<ExchangeRequest[]>([]);
const loading = ref(true);
const error = ref("");

async function load(): Promise<void> {
  loading.value = true;
  try {
    exchanges.value = await fetchMyExchanges();
  } catch (err) {
    error.value = toAppError(err).message;
  } finally {
    loading.value = false;
  }
}

async function cancel(item: ExchangeRequest): Promise<void> {
  try {
    const updated = await cancelExchange(item.id);
    const index = exchanges.value.findIndex((row) => row.id === item.id);
    if (index >= 0) exchanges.value[index] = updated;
    toast.show("Đã hủy yêu cầu đổi hàng.", "success");
  } catch (err) {
    toast.show(toAppError(err).message, "error");
  }
}

async function confirmReceived(item: ExchangeRequest): Promise<void> {
  try {
    const updated = await confirmReplacementReceived(item.id);
    const index = exchanges.value.findIndex((row) => row.id === item.id);
    if (index >= 0) exchanges.value[index] = updated;
    toast.show("Đã xác nhận nhận sản phẩm đổi.", "success");
  } catch (err) {
    toast.show(toAppError(err).message, "error");
  }
}

function historyLabel(status: string): string {
  if (status in exchangeStatusLabels) return exchangeStatusLabels[status as ExchangeStatus];
  return status;
}

onMounted(() => void load());
</script>

<template>
  <StorefrontLayout>
    <main class="mx-auto min-h-[70vh] max-w-5xl px-4 py-10 sm:px-6 lg:px-8">
      <div class="flex flex-wrap items-end justify-between gap-4 border-b border-white/10 pb-6">
        <div>
          <p class="text-xs font-black tracking-[0.2em] text-emerald-400 uppercase">Hậu mãi</p>
          <h1 class="mt-2 text-3xl font-black text-white">Yêu cầu đổi hàng</h1>
          <p class="mt-2 text-sm text-slate-400">
            Theo dõi quá trình duyệt, kiểm hàng và giao biến thể thay thế.
          </p>
        </div>
        <AppLink
          to="/orders"
          class="rounded-xl border border-white/10 px-4 py-2 text-sm font-bold text-slate-200 no-underline hover:bg-white/5"
          >Chọn đơn để đổi</AppLink
        >
      </div>
      <p v-if="loading" class="py-16 text-center text-slate-400">Đang tải yêu cầu…</p>
      <AppAlert v-else-if="error" class="mt-6" variant="error" title="Không tải được yêu cầu">{{
        error
      }}</AppAlert>
      <div v-else-if="exchanges.length" class="mt-6 space-y-4">
        <article
          v-for="item in exchanges"
          :key="item.id"
          class="rounded-3xl border border-white/10 bg-[#12151e] p-5 sm:p-6"
        >
          <div class="flex flex-wrap items-start justify-between gap-3">
            <div>
              <p class="font-mono text-xs text-slate-500">
                EX-{{ item.id }} · Đơn {{ item.order_number }}
              </p>
              <h2 class="mt-1 font-black text-white">{{ item.reason }}</h2>
            </div>
            <span
              class="rounded-full px-3 py-1 text-xs font-black uppercase"
              :class="exchangeStatusClass(item.status)"
              >{{ exchangeStatusLabels[item.status] }}</span
            >
          </div>
          <div class="mt-5 space-y-2 border-t border-white/10 pt-4">
            <div
              v-for="line in item.items"
              :key="line.id"
              class="flex flex-wrap justify-between gap-2 text-sm"
            >
              <span class="text-slate-300">{{ line.product_name }} × {{ line.quantity }}</span
              ><span class="font-bold text-emerald-400"
                >{{ line.source_size }}/{{ line.source_color }} → {{ line.target_size }}/{{
                  line.target_color
                }}</span
              >
            </div>
          </div>
          <div
            v-if="item.tracking_number"
            class="mt-4 rounded-xl bg-emerald-500/10 p-3 text-xs text-emerald-300"
          >
            Mã vận đơn giao đổi: <strong>{{ item.tracking_number }}</strong>
          </div>
          <ol
            v-if="item.status_history.length"
            class="mt-4 grid gap-2 border-t border-white/10 pt-4 sm:grid-cols-2"
          >
            <li v-for="event in item.status_history" :key="event.id" class="text-xs text-slate-400">
              <span class="font-bold text-slate-200">{{ historyLabel(event.to_status) }}</span>
              · {{ new Date(event.created_at).toLocaleString("vi-VN") }}
            </li>
          </ol>
          <div class="mt-4 flex justify-end">
            <BaseButton
              v-if="item.status === 'pending'"
              size="sm"
              variant="danger"
              @click="cancel(item)"
              >Hủy yêu cầu</BaseButton
            >
            <BaseButton
              v-else-if="item.status === 'replacement_shipped'"
              size="sm"
              @click="confirmReceived(item)"
              >Đã nhận sản phẩm đổi</BaseButton
            >
          </div>
        </article>
      </div>
      <div v-else class="mt-6 rounded-3xl border border-dashed border-white/15 p-12 text-center">
        <h2 class="font-black text-white">Chưa có yêu cầu đổi hàng</h2>
        <p class="mt-2 text-sm text-slate-400">Mở đơn đã hoàn tất để chọn sản phẩm cần đổi.</p>
      </div>
    </main>
  </StorefrontLayout>
</template>
