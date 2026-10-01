<script setup lang="ts">
import { computed, onMounted, ref } from "vue";
import { useRoute, useRouter } from "vue-router";

import BaseButton from "@/components/base/BaseButton.vue";
import AppAlert from "@/components/feedback/AppAlert.vue";
import AppPopup from "@/components/feedback/AppPopup.vue";
import AppLink from "@/components/navigation/AppLink.vue";
import AppLayout from "@/layouts/AppLayout.vue";
import { useToastStore } from "@/app/stores/toast";
import { toAppError } from "@/lib/http/errors";
import {
  cancelOrder,
  confirmOrderReceived,
  createOrderPaymentAttempt,
  fetchOrderDetail,
  fetchOrderPayment,
  verifyVnpayReturn,
  type OrderPaymentInfo,
} from "@/modules/cart/api";
import type { Order, OrderStatus } from "@/modules/cart/types";
import { confirmReplacementReceived, fetchMyExchanges } from "@/modules/exchanges/api";
import { exchangeStatusClass, exchangeStatusLabels } from "@/modules/exchanges/status";
import type { ExchangeRequest, ExchangeStatus } from "@/modules/exchanges/types";
import { canPayOrderWithVnpay } from "../payment";

const route = useRoute();
const router = useRouter();
const toast = useToastStore();

const orderId = computed(() => Number(route.params.id));
const order = ref<Order | null>(null);
const paymentInfo = ref<OrderPaymentInfo | null>(null);
const orderExchanges = ref<ExchangeRequest[]>([]);
const confirmingExchangeId = ref<number | null>(null);
const loading = ref(true);
const error = ref("");

const showCancelConfirm = ref(false);
const cancelLoading = ref(false);
const showReceivedConfirm = ref(false);
const receivedLoading = ref(false);
const payingOnline = ref(false);
const canPayOnline = computed(() => canPayOrderWithVnpay(order.value));

function formatCurrency(amount: string | number | undefined): string {
  if (amount === undefined) return "0 ₫";
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

function exchangeHistoryLabel(status: string): string {
  if (status in exchangeStatusLabels) return exchangeStatusLabels[status as ExchangeStatus];
  return status;
}

function statusBadge(status: OrderStatus) {
  switch (status) {
    case "pending_confirmation":
      return { label: "Chờ xác nhận", color: "border-amber-500/30 bg-amber-500/15 text-amber-400" };
    case "confirmed":
      return { label: "Đã xác nhận", color: "border-blue-500/30 bg-blue-500/15 text-blue-400" };
    case "preparing":
      return {
        label: "Đang xử lý",
        color: "border-indigo-500/30 bg-indigo-500/15 text-indigo-400",
      };
    case "shipped":
      return {
        label: "Đang giao hàng",
        color: "border-purple-500/30 bg-purple-500/15 text-purple-400",
      };
    case "completed":
      return {
        label: "Giao thành công",
        color: "border-emerald-500/30 bg-emerald-500/15 text-emerald-400",
      };
    case "cancelled":
      return { label: "Đã hủy", color: "border-rose-500/30 bg-rose-500/15 text-rose-400" };
    default:
      return { label: status, color: "border-slate-500/30 bg-slate-500/15 text-slate-300" };
  }
}

async function loadOrder() {
  if (isNaN(orderId.value)) return;
  loading.value = true;
  error.value = "";
  try {
    const [orderRes, exchanges] = await Promise.all([
      fetchOrderDetail(orderId.value),
      fetchMyExchanges(),
    ]);
    order.value = orderRes;
    orderExchanges.value = exchanges.filter((item) => item.order === orderRes.id);
    if (orderRes.payment_method === "vnpay") {
      try {
        paymentInfo.value = await fetchOrderPayment(orderId.value);
      } catch {
        paymentInfo.value = null;
      }
    } else {
      paymentInfo.value = null;
    }
  } catch (err) {
    error.value = toAppError(err).message;
  } finally {
    loading.value = false;
  }
}

async function confirmExchangeReceived(exchange: ExchangeRequest): Promise<void> {
  confirmingExchangeId.value = exchange.id;
  try {
    const updated = await confirmReplacementReceived(exchange.id);
    const index = orderExchanges.value.findIndex((item) => item.id === updated.id);
    if (index >= 0) orderExchanges.value[index] = updated;
    toast.show("Đã xác nhận nhận sản phẩm đổi.", "success");
  } catch (err) {
    toast.show(toAppError(err).message, "error");
  } finally {
    confirmingExchangeId.value = null;
  }
}

async function handlePayOnline() {
  if (!order.value || !canPayOnline.value) return;
  payingOnline.value = true;
  try {
    const idempotencyKey = globalThis.crypto.randomUUID();
    const result = await createOrderPaymentAttempt(order.value.id, idempotencyKey, {
      return_url: `${globalThis.location.origin}/orders/${String(order.value.id)}`,
    });
    if (result.checkout_url) {
      globalThis.location.assign(result.checkout_url);
    } else {
      toast.show("Không nhận được URL thanh toán từ cổng VNPay.", "error");
    }
  } catch (err) {
    toast.show(toAppError(err).message, "error");
  } finally {
    payingOnline.value = false;
  }
}

async function handleVnpayReturn(): Promise<void> {
  const responseCode =
    typeof route.query.vnp_ResponseCode === "string" ? route.query.vnp_ResponseCode : "";
  if (!responseCode) return;
  try {
    const params: Record<string, string> = {};
    for (const [key, value] of Object.entries(route.query)) {
      if (key.startsWith("vnp_") && typeof value === "string") params[key] = value;
    }
    const result = await verifyVnpayReturn(orderId.value, params);
    await loadOrder();
    if (result.payment_status === "paid") {
      toast.show("Thanh toán VNPay thành công.", "success");
    } else if (responseCode !== "00") {
      toast.show(`Thanh toán VNPay không thành công (mã ${responseCode}).`, "error");
    } else {
      toast.show("Chưa thể xác nhận giao dịch VNPay. Vui lòng liên hệ cửa hàng.", "info");
    }
  } catch (err) {
    toast.show(toAppError(err).message, "error");
  } finally {
    await router.replace({ name: "order-detail", params: { id: orderId.value } });
  }
}

async function handleConfirmReceived(): Promise<void> {
  if (!order.value) return;
  receivedLoading.value = true;
  try {
    order.value = await confirmOrderReceived(order.value.id);
    showReceivedConfirm.value = false;
    toast.show("Đã xác nhận nhận hàng. Bạn có thể đánh giá sản phẩm ngay.", "success");
  } catch (err) {
    toast.show(toAppError(err).message, "error");
  } finally {
    receivedLoading.value = false;
  }
}

async function handleCancelOrder() {
  if (!order.value) return;
  cancelLoading.value = true;
  try {
    const updated = await cancelOrder(order.value.id);
    order.value = updated;
    toast.show("Đã hủy đơn hàng và hoàn lại số lượng tồn kho.", "success");
    showCancelConfirm.value = false;
  } catch (err) {
    toast.show(toAppError(err).message || "Không thể hủy đơn hàng này.", "error");
  } finally {
    cancelLoading.value = false;
  }
}

onMounted(async () => {
  await loadOrder();
  await handleVnpayReturn();
});
</script>

<template>
  <AppLayout>
    <div class="space-y-6 max-w-4xl mx-auto">
      <!-- Back Navigation -->
      <div>
        <AppLink
          to="/orders"
          class="inline-flex items-center gap-2 text-xs font-bold uppercase tracking-wider text-slate-400 hover:text-emerald-400 no-underline"
        >
          ← Quay lại danh sách đơn hàng
        </AppLink>
      </div>

      <AppAlert v-if="error" variant="error" title="Không tìm thấy đơn hàng">{{ error }}</AppAlert>

      <!-- Loading State -->
      <div v-if="loading" class="p-12 text-center text-slate-400" role="status">
        <svg
          class="mx-auto h-8 w-8 animate-spin text-emerald-400 mb-3"
          viewBox="0 0 24 24"
          fill="none"
        >
          <circle
            class="opacity-25"
            cx="12"
            cy="12"
            r="10"
            stroke="currentColor"
            stroke-width="4"
          />
          <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8v8H4z" />
        </svg>
        <span class="text-sm font-semibold">Đang tải thông tin đơn hàng…</span>
      </div>

      <!-- Order Detail Content -->
      <div v-else-if="order" class="space-y-6">
        <!-- Header Banner -->
        <div
          class="rounded-3xl border border-white/10 bg-[#12151e]/85 backdrop-blur-xl p-6 sm:p-8 shadow-2xl space-y-4"
        >
          <div
            class="flex flex-wrap items-center justify-between gap-4 border-b border-white/10 pb-5"
          >
            <div>
              <div class="flex items-center gap-3">
                <h1 class="text-2xl font-black uppercase text-white">Đơn Hàng #{{ order.id }}</h1>
                <span
                  :class="[
                    'rounded-full border px-3 py-1 text-xs font-extrabold uppercase tracking-wider',
                    statusBadge(order.status).color,
                  ]"
                >
                  {{ statusBadge(order.status).label }}
                </span>
              </div>
              <p class="text-xs text-slate-400 mt-1">Đặt lúc: {{ formatDate(order.created_at) }}</p>
            </div>

            <!-- Cancel Button if pending -->
            <div v-if="order.status === 'pending_confirmation'">
              <BaseButton
                size="sm"
                variant="ghost"
                class="rounded-xl border border-rose-500/30 bg-rose-500/10 text-rose-400 hover:bg-rose-500/20 text-xs font-bold uppercase tracking-wider"
                @click="showCancelConfirm = true"
              >
                Hủy đơn hàng
              </BaseButton>
            </div>
            <BaseButton
              v-if="order.status === 'shipped'"
              size="sm"
              variant="primary"
              class="text-xs font-black tracking-wider uppercase"
              @click="showReceivedConfirm = true"
            >
              Đã nhận được hàng
            </BaseButton>
            <AppLink
              v-if="order.status === 'completed'"
              :to="{ name: 'exchange-create', query: { order: order.id } }"
              class="inline-flex min-h-10 items-center rounded-xl border border-emerald-500/30 bg-emerald-500/10 px-4 text-xs font-black tracking-wider text-emerald-400 uppercase no-underline hover:bg-emerald-500/20"
            >
              Yêu cầu đổi hàng
            </AppLink>
          </div>

          <!-- Shipping Address Snapshot -->
          <div class="grid gap-6 sm:grid-cols-2 pt-2">
            <div class="space-y-1">
              <p class="text-xs font-bold uppercase tracking-wider text-emerald-400">
                Địa chỉ giao hàng
              </p>
              <p class="text-sm font-bold text-white">
                {{ order.recipient_name || order.shipping_address?.recipient_name }}
              </p>
              <p class="text-xs text-slate-300">
                {{ order.phone_number || order.shipping_address?.phone_number }}
              </p>
              <p class="text-xs text-slate-400">
                {{ order.street_address || order.shipping_address?.street_address }},
                {{ order.ward || order.shipping_address?.ward }},
                {{ order.district || order.shipping_address?.district }},
                {{ order.province || order.shipping_address?.province }}
              </p>
            </div>

            <div class="space-y-1">
              <p class="text-xs font-bold uppercase tracking-wider text-emerald-400">
                Phương thức thanh toán
              </p>
              <p class="text-sm font-bold text-white uppercase">
                {{
                  order.payment_method === "vnpay"
                    ? "Cổng VNPay (Thanh toán trực tuyến)"
                    : `${order.payment_method} (Thanh toán khi nhận hàng)`
                }}
              </p>
              <p class="text-xs text-slate-400">
                Trạng thái:
                <span
                  :class="order.payment_status === 'paid' ? 'text-emerald-400' : 'text-amber-400'"
                  class="font-semibold uppercase"
                >
                  {{
                    order.payment_status === "paid"
                      ? "Đã thanh toán"
                      : order.payment_status || "Chưa thanh toán"
                  }}
                </span>
              </p>
              <!-- Pay with VNPay button if online payment pending -->
              <div v-if="canPayOnline" class="pt-2">
                <BaseButton
                  size="sm"
                  variant="primary"
                  :loading="payingOnline"
                  class="gap-2 text-xs font-bold uppercase tracking-wider"
                  @click="handlePayOnline"
                >
                  <svg class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path
                      stroke-linecap="round"
                      stroke-linejoin="round"
                      stroke-width="2"
                      d="M3 10h18M7 15h1m4 0h1m-7 4h12a3 3 0 003-3V8a3 3 0 00-3-3H6a3 3 0 00-3 3v8a3 3 0 003 3z"
                    />
                  </svg>
                  Thanh Toán VNPay
                </BaseButton>
              </div>
            </div>
          </div>
        </div>

        <section
          v-if="orderExchanges.length"
          class="rounded-3xl border border-sky-500/20 bg-sky-500/5 p-6 sm:p-8"
        >
          <div class="flex flex-wrap items-center justify-between gap-3">
            <div>
              <p class="text-xs font-black tracking-wider text-sky-300 uppercase">
                Luồng đổi hàng của đơn này
              </p>
              <h2 class="mt-1 text-lg font-black text-white">
                Không tạo đơn mới, theo dõi tại đơn gốc
              </h2>
            </div>
            <AppLink
              to="/exchanges"
              class="text-xs font-bold text-sky-300 no-underline hover:text-sky-200"
              >Xem tất cả yêu cầu →</AppLink
            >
          </div>
          <article
            v-for="exchange in orderExchanges"
            :key="exchange.id"
            class="mt-4 rounded-2xl border border-white/10 bg-black/20 p-4"
          >
            <div class="flex flex-wrap items-center justify-between gap-3">
              <span class="font-mono text-sm font-black text-white">EX-{{ exchange.id }}</span>
              <span
                class="rounded-full px-3 py-1 text-xs font-black uppercase"
                :class="exchangeStatusClass(exchange.status)"
                >{{ exchangeStatusLabels[exchange.status] }}</span
              >
            </div>
            <p v-if="exchange.tracking_number" class="mt-3 text-sm text-slate-300">
              Mã vận đơn hàng đổi:
              <strong class="text-white">{{ exchange.tracking_number }}</strong>
            </p>
            <ol class="mt-3 grid gap-2 sm:grid-cols-2">
              <li
                v-for="event in exchange.status_history"
                :key="event.id"
                class="text-xs text-slate-400"
              >
                <span class="font-bold text-slate-200">{{
                  exchangeHistoryLabel(event.to_status)
                }}</span>
                · {{ formatDate(event.created_at) }}
              </li>
            </ol>
            <BaseButton
              v-if="exchange.status === 'replacement_shipped'"
              class="mt-4"
              size="sm"
              :loading="confirmingExchangeId === exchange.id"
              @click="confirmExchangeReceived(exchange)"
              >Đã nhận sản phẩm đổi</BaseButton
            >
          </article>
        </section>

        <!-- Purchased Items List -->
        <div
          class="rounded-3xl border border-white/10 bg-[#12151e]/85 backdrop-blur-xl p-6 sm:p-8 shadow-2xl space-y-4"
        >
          <h2 class="text-base font-black uppercase text-white border-b border-white/10 pb-4">
            Sản Phẩm Đã Đặt
          </h2>

          <div class="divide-y divide-white/5">
            <div
              v-for="item in order.items"
              :key="item.id"
              class="py-3.5 flex flex-wrap items-center justify-between gap-4"
            >
              <div>
                <p class="font-bold text-white text-sm sm:text-base">{{ item.product_name }}</p>
                <div class="flex items-center gap-2 text-xs text-slate-400 mt-0.5">
                  <span v-if="item.size_label" class="text-slate-300"
                    >Size: {{ item.size_label }}</span
                  >
                  <span v-if="item.size_label && item.color_name">•</span>
                  <span v-if="item.color_name" class="text-slate-300"
                    >Màu: {{ item.color_name }}</span
                  >
                  <template v-if="item.sku">
                    <span>•</span>
                    <span class="font-mono text-emerald-400">SKU: {{ item.sku }}</span>
                  </template>
                </div>
              </div>

              <div class="text-right">
                <p class="text-xs text-slate-400 font-mono">
                  {{ formatCurrency(item.unit_price) }} x {{ item.quantity }}
                </p>
                <p class="font-mono text-sm sm:text-base font-bold text-white">
                  {{ formatCurrency(item.line_total) }}
                </p>
                <AppLink
                  v-if="order.status === 'completed'"
                  :to="{
                    name: 'product-detail',
                    params: { slug: item.product_slug },
                    hash: '#reviews',
                  }"
                  class="mt-2 inline-flex text-xs font-bold text-emerald-400 no-underline hover:text-emerald-300"
                >
                  Đánh giá sản phẩm
                </AppLink>
              </div>
            </div>
          </div>

          <!-- Total Calculation -->
          <div class="border-t border-white/10 pt-4 space-y-2 text-xs sm:text-sm">
            <div class="flex items-center justify-between text-slate-300">
              <span>Tạm tính</span>
              <span class="font-mono text-white font-bold">{{
                formatCurrency(order.subtotal)
              }}</span>
            </div>
            <div class="flex items-center justify-between text-slate-300">
              <span>Phí vận chuyển</span>
              <span class="font-mono text-white font-bold">
                {{
                  Number(order.shipping_fee) === 0 ? "Miễn phí" : formatCurrency(order.shipping_fee)
                }}
              </span>
            </div>
            <div
              v-if="Number(order.discount_total) > 0"
              class="flex items-center justify-between text-emerald-400"
            >
              <span>Giảm giá</span>
              <span class="font-mono font-bold">-{{ formatCurrency(order.discount_total) }}</span>
            </div>
            <div
              class="flex items-center justify-between border-t border-white/10 pt-3 text-base font-black"
            >
              <span class="text-white uppercase">Tổng thanh toán</span>
              <span class="font-mono text-xl text-emerald-400">{{
                formatCurrency(order.total)
              }}</span>
            </div>
          </div>
        </div>

        <!-- Order Timeline / Status History -->
        <div
          v-if="order.status_history && order.status_history.length > 0"
          class="rounded-3xl border border-white/10 bg-[#12151e]/85 backdrop-blur-xl p-6 sm:p-8 shadow-2xl space-y-4"
        >
          <h2 class="text-base font-black uppercase text-white border-b border-white/10 pb-4">
            Nhật Ký Trạng Thái Đơn Hàng
          </h2>

          <div class="space-y-3">
            <div
              v-for="hist in order.status_history"
              :key="hist.id"
              class="flex items-start gap-3 text-xs"
            >
              <div
                class="mt-1 h-2 w-2 rounded-full bg-emerald-400 flex-shrink-0 shadow-[0_0_8px_#10b981]"
              />
              <div class="flex-1">
                <p class="text-slate-200">
                  Chuyển trạng thái từ
                  <span class="font-bold text-white">{{ hist.from_status }}</span> ➔
                  <span class="font-bold text-emerald-400">{{ hist.to_status }}</span>
                </p>
                <p v-if="hist.reason" class="text-slate-400 italic mt-0.5">"{{ hist.reason }}"</p>
              </div>
              <span class="text-slate-500 font-mono">{{ formatDate(hist.created_at) }}</span>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Confirm Cancel Modal -->
    <AppPopup
      v-model="showCancelConfirm"
      mode="confirm"
      variant="error"
      title="Xác nhận hủy đơn hàng"
      :message="`Bạn có chắc chắn muốn hủy đơn hàng #${order?.id}? Toàn bộ số lượng giày sẽ được hoàn lại kho ngay lập tức.`"
      action-text="Hủy đơn ngay"
      cancel-text="Giữ đơn hàng"
      :loading="cancelLoading"
      @confirm="handleCancelOrder"
    />
    <AppPopup
      v-model="showReceivedConfirm"
      mode="confirm"
      variant="success"
      title="Xác nhận đã nhận hàng"
      message="Chỉ xác nhận khi bạn đã nhận và kiểm tra sản phẩm. Sau bước này đơn hàng sẽ hoàn tất và có thể đánh giá."
      action-text="Xác nhận đã nhận"
      cancel-text="Để sau"
      :loading="receivedLoading"
      @confirm="handleConfirmReceived"
    />
  </AppLayout>
</template>
