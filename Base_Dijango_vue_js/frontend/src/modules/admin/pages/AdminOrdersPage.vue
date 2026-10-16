<script setup lang="ts">
import { onBeforeUnmount, onMounted, ref } from "vue";

import BaseButton from "@/components/base/BaseButton.vue";
import BaseInput from "@/components/base/BaseInput.vue";
import BasePagination from "@/components/base/BasePagination.vue";
import AppAlert from "@/components/feedback/AppAlert.vue";
import AdminLayout from "@/layouts/AdminLayout.vue";
import { useToastStore } from "@/app/stores/toast";
import { toAppError } from "@/lib/http/errors";
import { fetchAdminOrders, transitionAdminOrder, type AdminOrderListItem } from "../api";

const toast = useToastStore();
const orders = ref<AdminOrderListItem[]>([]);
const loading = ref(true);
const error = ref("");
const statusFilter = ref<string>("");
const search = ref("");
const startDate = ref("");
const endDate = ref("");
const todayOnly = ref(false);
const page = ref(1);
const count = ref(0);

// Transition state
const showTransitionModal = ref(false);
const transitionLoading = ref(false);
const selectedOrder = ref<AdminOrderListItem | null>(null);
const targetStatus = ref<string>("");
const transitionNote = ref<string>("");

// Order detail modal state
const showDetailModal = ref(false);
const viewingOrder = ref<AdminOrderListItem | null>(null);

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

function paymentMethodLabel(value: string): string {
  return value === "vnpay" ? "VNPay" : value === "cod" ? "Thanh toán khi nhận hàng" : value;
}

function paymentStatusLabel(value: string): string {
  return (
    {
      pending: "Chờ thanh toán",
      paid: "Đã thanh toán",
      failed: "Thất bại",
      cancelled: "Đã hủy",
    }[value] ?? value
  );
}

function statusBadge(status: string) {
  switch (status) {
    case "pending_confirmation":
      return { label: "Chờ xác nhận", color: "border-amber-500/30 bg-amber-500/15 text-amber-400" };
    case "confirmed":
      return { label: "Đã xác nhận", color: "border-blue-500/30 bg-blue-500/15 text-blue-400" };
    case "preparing":
      return {
        label: "Đang chuẩn bị",
        color: "border-indigo-500/30 bg-indigo-500/15 text-indigo-400",
      };
    case "shipped":
      return { label: "Đang giao", color: "border-purple-500/30 bg-purple-500/15 text-purple-400" };
    case "delivered":
      return { label: "Đã giao", color: "border-cyan-500/30 bg-cyan-500/15 text-cyan-400" };
    case "completed":
      return {
        label: "Hoàn tất",
        color: "border-emerald-500/30 bg-emerald-500/15 text-emerald-400",
      };
    case "cancelled":
      return { label: "Đã hủy", color: "border-rose-500/30 bg-rose-500/15 text-rose-400" };
    default:
      return { label: status, color: "border-slate-500/30 bg-slate-500/15 text-slate-300" };
  }
}

function nextAvailableTransitions(status: string): Array<{ value: string; label: string }> {
  switch (status) {
    case "pending_confirmation":
      return [
        { value: "confirmed", label: "Xác nhận đơn" },
        { value: "cancelled", label: "Hủy đơn" },
      ];
    case "confirmed":
      return [
        { value: "preparing", label: "Đóng gói" },
        { value: "cancelled", label: "Hủy đơn" },
      ];
    case "preparing":
      return [
        { value: "shipped", label: "Giao vận" },
        { value: "cancelled", label: "Hủy đơn" },
      ];
    case "shipped":
      return [{ value: "delivered", label: "Xác nhận đã giao" }];
    case "delivered":
      return [];
    default:
      return [];
  }
}

async function loadOrders() {
  loading.value = true;
  error.value = "";
  try {
    const response = await fetchAdminOrders({
      page: page.value,
      status: statusFilter.value || undefined,
      search: search.value || undefined,
      start_date: startDate.value || undefined,
      end_date: endDate.value || undefined,
      today: todayOnly.value || undefined,
    });
    orders.value = response.results;
    count.value = response.count;
  } catch (err) {
    error.value = toAppError(err).message;
  } finally {
    loading.value = false;
  }
}

async function applyFilters(): Promise<void> {
  page.value = 1;
  await loadOrders();
}

async function clearFilters(): Promise<void> {
  search.value = "";
  startDate.value = "";
  endDate.value = "";
  statusFilter.value = "";
  todayOnly.value = false;
  await applyFilters();
}

async function changePage(value: number): Promise<void> {
  page.value = value;
  await loadOrders();
}

function handleRealtime(event: Event): void {
  const detail = (event as CustomEvent<{ payload?: { kind?: string } }>).detail;
  if (detail.payload?.kind === "order") void loadOrders();
}

function openTransition(order: AdminOrderListItem, toStatus: string) {
  selectedOrder.value = order;
  targetStatus.value = toStatus;
  transitionNote.value = "";
  showTransitionModal.value = true;
}

async function handleTransitionSubmit() {
  if (!selectedOrder.value || !targetStatus.value) return;
  transitionLoading.value = true;
  try {
    const updated = await transitionAdminOrder(selectedOrder.value.id, {
      to_status: targetStatus.value,
      expected_updated_at: selectedOrder.value.updated_at,
      note: transitionNote.value.trim() || undefined,
    });

    const idx = orders.value.findIndex((o) => o.id === updated.id);
    if (idx !== -1) {
      orders.value[idx] = updated;
    }
    toast.show(
      `Đã chuyển trạng thái đơn hàng #${String(updated.number || updated.id)} sang "${statusBadge(updated.status).label}".`,
      "success",
    );
    showTransitionModal.value = false;
    selectedOrder.value = null;
  } catch (err) {
    toast.show(toAppError(err).message, "error");
  } finally {
    transitionLoading.value = false;
  }
}

function openDetail(order: AdminOrderListItem) {
  viewingOrder.value = order;
  showDetailModal.value = true;
}

onMounted(() => {
  globalThis.addEventListener("hai-duy:realtime", handleRealtime);
  void loadOrders();
});
onBeforeUnmount(() => {
  globalThis.removeEventListener("hai-duy:realtime", handleRealtime);
});
</script>

<template>
  <AdminLayout>
    <div class="space-y-6">
      <!-- Page Header -->
      <div class="space-y-5 border-b border-white/10 pb-5">
        <div>
          <p class="text-xs font-bold uppercase tracking-widest text-emerald-400">
            Vận Hành & Xử Lý Đơn
          </p>
          <h1 class="text-2xl sm:text-3xl font-black uppercase tracking-tight text-white mt-1">
            Quản Lý Đơn Hàng
          </h1>
          <p class="text-sm text-slate-400 mt-1">
            Theo dõi tất cả đơn hàng, duyệt đơn, chuyển trạng thái đóng gói giao hàng và hoàn tồn tự
            động khi hủy.
          </p>
        </div>

        <div
          class="grid gap-3 md:grid-cols-2 xl:grid-cols-[minmax(20rem,1.6fr)_minmax(10rem,.7fr)_minmax(10rem,.7fr)_minmax(12rem,.8fr)_auto_auto_auto] xl:items-center"
        >
          <BaseInput
            v-model="search"
            id="order-search"
            name="order_search"
            placeholder="Mã đơn, email, người nhận"
            aria-label="Tìm đơn hàng"
            clearable
            @keyup.enter="applyFilters"
          />
          <BaseInput
            v-model="startDate"
            id="order-start-date"
            name="start_date"
            type="date"
            aria-label="Từ ngày"
          />
          <BaseInput
            v-model="endDate"
            id="order-end-date"
            name="end_date"
            type="date"
            aria-label="Đến ngày"
          />
          <!-- Filter by status -->
          <select
            v-model="statusFilter"
            class="min-h-12 rounded-xl border border-[var(--color-border)] bg-[var(--color-input-bg)] px-3 text-sm font-semibold text-[var(--color-text)] focus:border-emerald-500 focus:outline-none"
            @change="applyFilters"
          >
            <option value="" class="bg-[#12151e] text-white">Tất cả trạng thái</option>
            <option value="pending_confirmation" class="bg-[#12151e] text-amber-400">
              Chờ xác nhận
            </option>
            <option value="confirmed" class="bg-[#12151e] text-blue-400">Đã xác nhận</option>
            <option value="preparing" class="bg-[#12151e] text-indigo-400">Đang chuẩn bị</option>
            <option value="shipped" class="bg-[#12151e] text-purple-400">Đang giao</option>
            <option value="delivered" class="bg-[#12151e] text-cyan-400">Đã giao</option>
            <option value="completed" class="bg-[#12151e] text-emerald-400">Hoàn tất</option>
            <option value="cancelled" class="bg-[#12151e] text-rose-400">Đã hủy</option>
          </select>

          <BaseButton size="md" @click="applyFilters">
            <span class="whitespace-nowrap">Lọc danh sách</span>
          </BaseButton>

          <BaseButton
            size="md"
            :variant="todayOnly ? 'primary' : 'secondary'"
            @click="
              todayOnly = !todayOnly;
              applyFilters();
            "
          >
            <span class="whitespace-nowrap">Đơn hôm nay</span>
          </BaseButton>
          <BaseButton size="md" variant="secondary" @click="clearFilters">
            <span class="whitespace-nowrap">Xóa bộ lọc</span>
          </BaseButton>
        </div>
      </div>

      <AppAlert v-if="error" variant="error" title="Lỗi tải đơn hàng">{{ error }}</AppAlert>

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
        <span class="text-sm font-semibold">Đang tải danh sách đơn hàng…</span>
      </div>

      <!-- Empty State -->
      <div
        v-else-if="orders.length === 0"
        class="rounded-3xl border border-dashed border-white/15 bg-white/5 p-12 text-center"
      >
        <div
          class="mx-auto mb-3 flex h-14 w-14 items-center justify-center rounded-2xl bg-white/5 text-slate-400"
        >
          <svg class="h-7 w-7" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path
              stroke-linecap="round"
              stroke-linejoin="round"
              stroke-width="1.5"
              d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2"
            />
          </svg>
        </div>
        <h3 class="text-lg font-bold text-white">Chưa có đơn hàng nào</h3>
        <p class="mt-1 text-sm text-slate-400 max-w-md mx-auto">
          Hiện tại chưa có đơn hàng nào thỏa mãn bộ lọc đã chọn.
        </p>
      </div>

      <!-- Orders Table -->
      <div
        v-else
        class="overflow-hidden rounded-3xl border border-white/10 bg-[#12151e]/85 backdrop-blur-xl shadow-2xl"
      >
        <div class="overflow-x-auto">
          <table class="w-full text-left text-sm text-slate-300">
            <thead
              class="border-b border-white/10 bg-white/5 text-xs font-black uppercase tracking-wider text-slate-400"
            >
              <tr>
                <th class="px-6 py-4">Mã Đơn / Khách Hàng</th>
                <th class="px-6 py-4">Ngày Đặt</th>
                <th class="px-6 py-4">Sản Phẩm</th>
                <th class="px-6 py-4">Tổng Tiền / PTTT</th>
                <th class="px-6 py-4">Trạng Thái</th>
                <th class="px-6 py-4 text-right">Chuyển Trạng Thái</th>
              </tr>
            </thead>
            <tbody class="divide-y divide-white/5">
              <tr
                v-for="item in orders"
                :key="item.id"
                class="transition-colors hover:bg-white/[0.02]"
              >
                <td class="px-6 py-4">
                  <div class="font-mono font-bold text-white text-base">
                    #{{ item.number || item.id }}
                  </div>
                  <div class="text-xs text-slate-400 mt-0.5">
                    {{ item.customer_email || item.recipient_name || "Khách hàng" }}
                  </div>
                  <div v-if="item.phone_number" class="text-[11px] text-slate-500 font-mono">
                    SĐT: {{ item.phone_number }}
                  </div>
                </td>

                <td class="px-6 py-4 text-xs font-medium text-slate-400">
                  {{ formatDate(item.created_at) }}
                </td>

                <td class="px-6 py-4 text-xs">
                  <div class="font-semibold text-slate-200">
                    {{ item.items?.length || 0 }} loại sản phẩm
                  </div>
                  <button
                    type="button"
                    class="text-[11px] font-bold text-emerald-400 hover:underline mt-1 cursor-pointer"
                    @click="openDetail(item)"
                  >
                    Xem chi tiết &rarr;
                  </button>
                </td>

                <td class="px-6 py-4">
                  <div class="font-mono font-bold text-emerald-400 text-base">
                    {{ formatCurrency(item.total) }}
                  </div>
                  <div class="text-[11px] font-semibold text-slate-400 mt-0.5 uppercase">
                    {{ paymentMethodLabel(item.payment_method) }} •
                    {{ paymentStatusLabel(item.payment_status) }}
                  </div>
                </td>

                <td class="px-6 py-4">
                  <span
                    :class="[
                      'inline-flex items-center gap-1.5 rounded-full px-2.5 py-1 text-xs font-extrabold uppercase tracking-wider',
                      statusBadge(item.status).color,
                    ]"
                  >
                    {{ statusBadge(item.status).label }}
                  </span>
                </td>

                <td class="px-6 py-4 text-right">
                  <div class="flex flex-wrap items-center justify-end gap-1.5">
                    <template v-if="nextAvailableTransitions(item.status).length > 0">
                      <button
                        v-for="trans in nextAvailableTransitions(item.status)"
                        :key="trans.value"
                        type="button"
                        :class="[
                          'rounded-lg px-2.5 py-1 text-xs font-bold transition-all cursor-pointer',
                          trans.value === 'cancelled'
                            ? 'border border-rose-500/20 bg-rose-500/10 text-rose-400 hover:bg-rose-500/20'
                            : 'border border-emerald-500/30 bg-emerald-500/15 text-emerald-400 hover:bg-emerald-500/25',
                        ]"
                        @click="openTransition(item, trans.value)"
                      >
                        {{ trans.label }}
                      </button>
                    </template>
                    <span
                      v-if="nextAvailableTransitions(item.status).length === 0"
                      class="text-xs text-slate-500 italic"
                    >
                      Đơn đã đóng
                    </span>
                  </div>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
        <div class="border-t border-white/10 p-4">
          <BasePagination
            :count="count"
            :page="page"
            :disabled="loading"
            @update:page="changePage"
          />
        </div>
      </div>
    </div>

    <!-- Modal Chuyển Trạng Thái Đơn Hàng -->
    <Teleport to="body">
      <Transition name="popup-fade">
        <div
          v-if="showTransitionModal"
          class="fixed inset-0 z-50 flex items-center justify-center p-4 sm:p-6"
          role="dialog"
          aria-modal="true"
        >
          <div
            class="fixed inset-0 bg-black/80 backdrop-blur-md transition-opacity"
            aria-hidden="true"
            @click="!transitionLoading && (showTransitionModal = false)"
          />

          <div
            class="relative z-10 w-full max-w-md overflow-hidden rounded-3xl border border-white/15 bg-[#12151e] p-6 sm:p-8 text-white shadow-[0_25px_70px_rgba(0,0,0,0.95)]"
          >
            <h2 class="text-xl font-black uppercase tracking-tight text-white mb-2">
              Xác nhận chuyển trạng thái
            </h2>
            <p class="text-sm text-slate-300 mb-4">
              Đơn hàng:
              <span class="font-mono font-bold text-emerald-400"
                >#{{ selectedOrder?.number || selectedOrder?.id }}</span
              >
              <br />
              Chuyển sang:
              <span class="font-bold text-white">{{ statusBadge(targetStatus).label }}</span>
            </p>

            <div class="mb-4">
              <label class="block text-xs font-bold uppercase tracking-wider text-slate-300 mb-1.5">
                Ghi chú điều phối (tùy chọn)
              </label>
              <textarea
                v-model="transitionNote"
                rows="2"
                placeholder="Nhập ghi chú cho nhân viên bưu tá / lý do..."
                class="w-full rounded-xl border border-white/15 bg-white/5 p-3 text-sm text-white placeholder-slate-500 focus:border-emerald-500 focus:outline-none focus:ring-1 focus:ring-emerald-500 transition-colors"
              />
            </div>

            <div class="flex items-center justify-end gap-3 pt-4 border-t border-white/10">
              <BaseButton
                type="button"
                variant="ghost"
                class="rounded-xl border border-white/15 text-slate-300 hover:text-white text-xs font-bold uppercase"
                :disabled="transitionLoading"
                @click="showTransitionModal = false"
              >
                Hủy bỏ
              </BaseButton>
              <BaseButton
                type="button"
                :class="[
                  'rounded-xl text-xs font-black uppercase tracking-wider px-5',
                  targetStatus === 'cancelled'
                    ? 'bg-rose-600 hover:bg-rose-500 text-white shadow-[0_0_20px_rgba(244,63,94,0.35)]'
                    : 'bg-emerald-500 text-slate-950 hover:bg-emerald-400 shadow-[0_0_20px_rgba(16,185,129,0.3)]',
                ]"
                :loading="transitionLoading"
                @click="handleTransitionSubmit"
              >
                Xác nhận chuyển
              </BaseButton>
            </div>
          </div>
        </div>
      </Transition>
    </Teleport>

    <!-- Modal Chi Tiết Đơn Hàng -->
    <Teleport to="body">
      <Transition name="popup-fade">
        <div
          v-if="showDetailModal && viewingOrder"
          class="fixed inset-0 z-50 flex items-center justify-center p-4 sm:p-6"
          role="dialog"
          aria-modal="true"
        >
          <div
            class="fixed inset-0 bg-black/80 backdrop-blur-md transition-opacity"
            aria-hidden="true"
            @click="showDetailModal = false"
          />

          <div
            class="relative z-10 w-full max-w-2xl overflow-hidden rounded-3xl border border-white/15 bg-[#12151e] p-6 sm:p-8 text-white shadow-[0_25px_70px_rgba(0,0,0,0.95)] max-h-[90vh] overflow-y-auto"
          >
            <!-- Close button -->
            <button
              type="button"
              class="absolute top-5 right-5 flex h-8 w-8 items-center justify-center rounded-full text-slate-400 hover:bg-white/10 hover:text-white transition-colors cursor-pointer"
              @click="showDetailModal = false"
            >
              <svg
                class="h-4 w-4"
                fill="none"
                viewBox="0 0 24 24"
                stroke="currentColor"
                stroke-width="2.5"
              >
                <path stroke-linecap="round" stroke-linejoin="round" d="M6 18L18 6M6 6l12 12" />
              </svg>
            </button>

            <h2 class="text-xl font-black uppercase tracking-tight text-white mb-1">
              Chi Tiết Đơn Hàng #{{ viewingOrder.number || viewingOrder.id }}
            </h2>
            <p class="text-xs text-slate-400 mb-6">
              Đặt lúc: {{ formatDate(viewingOrder.created_at) }} • Khách hàng:
              {{ viewingOrder.customer_email || "N/A" }}
            </p>

            <!-- Items List -->
            <div class="space-y-3 mb-6">
              <h3 class="text-xs font-bold uppercase tracking-wider text-slate-400">
                Danh sách sản phẩm
              </h3>
              <div
                class="divide-y divide-white/10 rounded-2xl border border-white/10 bg-white/5 p-4"
              >
                <div
                  v-for="item in viewingOrder.items"
                  :key="item.id"
                  class="flex items-center justify-between py-2.5 first:pt-0 last:pb-0"
                >
                  <div>
                    <p class="text-sm font-bold text-white">{{ item.product_name }}</p>
                    <p class="text-xs text-slate-400 font-mono">
                      SKU: {{ item.sku }} • Size: {{ item.size_label || "Free" }} • Màu:
                      {{ item.color_name || "Mặc định" }}
                    </p>
                    <p class="text-xs text-slate-500">Số lượng: x{{ item.quantity }}</p>
                  </div>
                  <div class="font-mono font-bold text-sm text-white">
                    {{ formatCurrency(item.line_total) }}
                  </div>
                </div>
              </div>
            </div>

            <!-- Shipping Info -->
            <div class="mb-6 rounded-2xl border border-white/10 bg-white/5 p-4">
              <h3 class="text-xs font-bold uppercase tracking-wider text-slate-400 mb-2">
                Địa chỉ giao hàng
              </h3>
              <p class="text-sm font-semibold text-white">
                {{ viewingOrder.shipping_address?.recipient_name || viewingOrder.recipient_name }} -
                {{ viewingOrder.shipping_address?.phone_number || viewingOrder.phone_number }}
              </p>
              <p class="text-xs text-slate-400 mt-1">
                {{ viewingOrder.shipping_address?.street_address || viewingOrder.street_address }},
                {{ viewingOrder.shipping_address?.ward || viewingOrder.ward }},
                {{ viewingOrder.shipping_address?.district || viewingOrder.district }},
                {{ viewingOrder.shipping_address?.province || viewingOrder.province }}
              </p>
            </div>

            <!-- Status History -->
            <div
              v-if="viewingOrder.status_history && viewingOrder.status_history.length > 0"
              class="mb-6"
            >
              <h3 class="text-xs font-bold uppercase tracking-wider text-slate-400 mb-2">
                Lịch sử trạng thái
              </h3>
              <div class="space-y-2">
                <div
                  v-for="history in viewingOrder.status_history"
                  :key="history.id"
                  class="rounded-xl border border-white/5 bg-white/[0.02] p-2.5 text-xs flex items-center justify-between"
                >
                  <div>
                    <span class="font-bold text-emerald-400">{{ history.to_status }}</span>
                    <span v-if="history.note" class="text-slate-400 ml-2"
                      >({{ history.note }})</span
                    >
                    <span v-if="history.actor_email" class="text-slate-500 ml-1"
                      >bởi {{ history.actor_email }}</span
                    >
                  </div>
                  <div class="text-slate-500 font-mono text-[11px]">
                    {{ formatDate(history.created_at) }}
                  </div>
                </div>
              </div>
            </div>

            <div class="flex justify-end pt-2">
              <BaseButton
                type="button"
                variant="ghost"
                class="rounded-xl border border-white/15 text-slate-300 hover:text-white text-xs font-bold uppercase"
                @click="showDetailModal = false"
              >
                Đóng
              </BaseButton>
            </div>
          </div>
        </div>
      </Transition>
    </Teleport>
  </AdminLayout>
</template>

<style scoped>
.popup-fade-enter-active,
.popup-fade-leave-active {
  transition: opacity 0.2s ease;
}

.popup-fade-enter-active > div:last-child,
.popup-fade-leave-active > div:last-child {
  transition:
    transform 0.2s cubic-bezier(0.16, 1, 0.3, 1),
    opacity 0.2s ease;
}

.popup-fade-enter-from,
.popup-fade-leave-to {
  opacity: 0;
}

.popup-fade-enter-from > div:last-child {
  transform: scale(0.95) translateY(10px);
  opacity: 0;
}

.popup-fade-leave-to > div:last-child {
  transform: scale(0.98) translateY(4px);
  opacity: 0;
}
</style>
