<script setup lang="ts">
import { onMounted, ref } from "vue";

import BaseButton from "@/components/base/BaseButton.vue";
import AppAlert from "@/components/feedback/AppAlert.vue";
import AppLink from "@/components/navigation/AppLink.vue";
import AppLayout from "@/layouts/AppLayout.vue";
import { toAppError } from "@/lib/http/errors";
import { fetchMyOrders } from "@/modules/cart/api";
import type { Order, OrderStatus } from "@/modules/cart/types";

const orders = ref<Order[]>([]);
const loading = ref(true);
const error = ref("");

function formatCurrency(amount: string | number): string {
  const num = typeof amount === "string" ? Number(amount) : amount;
  return new Intl.NumberFormat("vi-VN", { style: "currency", currency: "VND" }).format(num);
}

function formatDate(dateStr: string): string {
  return new Date(dateStr).toLocaleString("vi-VN", {
    year: "numeric",
    month: "2-digit",
    day: "2-digit",
    hour: "2-digit",
    minute: "2-digit",
  });
}

function statusBadge(status: OrderStatus) {
  switch (status) {
    case "pending_confirmation":
      return { label: "Chờ xác nhận", color: "border-amber-500/30 bg-amber-500/15 text-amber-400" };
    case "confirmed":
      return { label: "Đã xác nhận", color: "border-blue-500/30 bg-blue-500/15 text-blue-400" };
    case "preparing":
      return { label: "Đang xử lý", color: "border-indigo-500/30 bg-indigo-500/15 text-indigo-400" };
    case "shipped":
      return { label: "Đang giao hàng", color: "border-purple-500/30 bg-purple-500/15 text-purple-400" };
    case "completed":
      return { label: "Giao thành công", color: "border-emerald-500/30 bg-emerald-500/15 text-emerald-400" };
    case "cancelled":
      return { label: "Đã hủy", color: "border-rose-500/30 bg-rose-500/15 text-rose-400" };
    default:
      return { label: status, color: "border-slate-500/30 bg-slate-500/15 text-slate-300" };
  }
}

async function loadOrders() {
  loading.value = true;
  error.value = "";
  try {
    orders.value = await fetchMyOrders();
  } catch (err) {
    error.value = toAppError(err).message;
  } finally {
    loading.value = false;
  }
}

onMounted(loadOrders);
</script>

<template>
  <AppLayout>
    <div class="space-y-6">
      <!-- Header -->
      <div class="space-y-1.5 border-b border-white/10 pb-5 flex flex-wrap items-center justify-between gap-4">
        <div>
          <p class="text-xs font-bold uppercase tracking-widest text-emerald-400">Lịch Sử Mua Sắm</p>
          <h1 class="text-2xl sm:text-3xl font-black uppercase tracking-tight text-white mt-1">
            Đơn Hàng Của Tôi
          </h1>
          <p class="text-sm text-slate-400">
            Theo dõi tình trạng vận chuyển và kiểm tra chi tiết các đơn đặt hàng COD.
          </p>
        </div>
        <BaseButton
          size="sm"
          variant="ghost"
          class="rounded-xl border border-white/15 text-slate-300 hover:text-white"
          @click="loadOrders"
        >
          Làm mới
        </BaseButton>
      </div>

      <AppAlert v-if="error" variant="error" title="Không thể tải đơn hàng">{{ error }}</AppAlert>

      <!-- Loading State -->
      <div v-if="loading" class="p-12 text-center text-slate-400" role="status">
        <svg class="mx-auto h-8 w-8 animate-spin text-emerald-400 mb-3" viewBox="0 0 24 24" fill="none">
          <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4" />
          <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8v8H4z" />
        </svg>
        <span class="text-sm font-semibold">Đang tải lịch sử đơn hàng…</span>
      </div>

      <!-- Empty State -->
      <div
        v-else-if="orders.length === 0"
        class="rounded-3xl border border-dashed border-white/15 bg-white/5 p-12 text-center text-white"
      >
        <div class="mx-auto mb-3 flex h-14 w-14 items-center justify-center rounded-2xl bg-white/5 text-slate-400">
          <svg class="h-7 w-7" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="1.5">
            <path stroke-linecap="round" stroke-linejoin="round" d="M16 11V7a4 4 0 00-8 0v4M5 9h14l1 12H4L5 9z" />
          </svg>
        </div>
        <h3 class="text-lg font-bold">Bạn chưa có đơn đặt hàng nào</h3>
        <p class="mt-1 text-sm text-slate-400 max-w-md mx-auto">
          Các đơn hàng sau khi đặt thành công sẽ được liệt kê đầy đủ tại đây để bạn tiện theo dõi.
        </p>
        <div class="mt-6">
          <AppLink
            to="/"
            class="inline-flex items-center gap-2 rounded-xl bg-emerald-500 px-6 py-3 text-xs font-black uppercase tracking-wider text-black no-underline hover:bg-emerald-400"
          >
            Mua sắm ngay
          </AppLink>
        </div>
      </div>

      <!-- Orders List -->
      <div v-else class="space-y-4">
        <div
          v-for="order in orders"
          :key="order.id"
          class="rounded-3xl border border-white/10 bg-[#12151e]/85 backdrop-blur-xl p-5 sm:p-6 shadow-xl transition-all hover:border-white/20"
        >
          <div class="flex flex-wrap items-center justify-between gap-3 border-b border-white/10 pb-4">
            <div class="flex items-center gap-3">
              <span class="font-mono text-sm sm:text-base font-black text-white">
                Đơn hàng #{{ order.id }}
              </span>
              <span
                :class="[
                  'rounded-full border px-2.5 py-0.5 text-xs font-extrabold uppercase tracking-wider',
                  statusBadge(order.status).color
                ]"
              >
                {{ statusBadge(order.status).label }}
              </span>
            </div>
            <span class="text-xs text-slate-400">
              {{ formatDate(order.created_at) }}
            </span>
          </div>

          <!-- Items Overview -->
          <div class="py-4 space-y-2">
            <div
              v-for="item in order.items"
              :key="item.id"
              class="flex items-center justify-between text-xs sm:text-sm text-slate-300"
            >
              <div class="flex items-center gap-2">
                <span class="font-bold text-white">{{ item.product_name }}</span>
                <span class="text-slate-400 font-mono">x{{ item.quantity }}</span>
                <span v-if="item.size_label" class="rounded bg-white/5 px-1.5 py-0.5 text-[10px] text-slate-300">
                  Size {{ item.size_label }}
                </span>
              </div>
              <span class="font-mono font-semibold text-slate-200">
                {{ formatCurrency(item.line_total) }}
              </span>
            </div>
          </div>

          <!-- Footer Total & Detail Action -->
          <div class="flex flex-wrap items-center justify-between gap-3 border-t border-white/10 pt-4">
            <div class="text-xs text-slate-400">
              Giao đến: <strong class="text-white">{{ order.recipient_name || order.shipping_address?.recipient_name || 'Khách hàng' }}</strong> ({{ order.street_address || order.shipping_address?.street_address || '' }})
            </div>
            <div class="flex items-center gap-4">
              <div class="text-right">
                <span class="text-xs text-slate-400 mr-2">Tổng tiền:</span>
                <span class="font-mono text-base font-black text-emerald-400">
                  {{ formatCurrency(order.total) }}
                </span>
              </div>
              <AppLink
                :to="'/orders/' + order.id"
                class="rounded-xl bg-white/10 px-4 py-2 text-xs font-bold uppercase tracking-wider text-white no-underline hover:bg-emerald-500 hover:text-black transition-all"
              >
                Xem chi tiết
              </AppLink>
            </div>
          </div>
        </div>
      </div>
    </div>
  </AppLayout>
</template>
