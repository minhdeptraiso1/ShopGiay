<script setup lang="ts">
import { computed, onMounted, ref } from "vue";

import BaseButton from "@/components/base/BaseButton.vue";
import AppAlert from "@/components/feedback/AppAlert.vue";
import AppLink from "@/components/navigation/AppLink.vue";
import AdminLayout from "@/layouts/AdminLayout.vue";
import { useToastStore } from "@/app/stores/toast";
import { toAppError } from "@/lib/http/errors";
import { useAuth } from "@/modules/auth/composables/useAuth";
import {
  adjustVariantInventory,
  fetchAdminProducts,
  fetchAdminVariants,
  fetchVariantStockMovements,
  type AdminProduct,
  type AdminVariant,
  type StockMovementItem,
} from "../api";

const toast = useToastStore();
const { user } = useAuth();
const variants = ref<AdminVariant[]>([]);
const products = ref<AdminProduct[]>([]);
const loading = ref(true);
const error = ref("");
const isAdmin = computed(() => user.value?.roles.includes("ADMIN") ?? false);
const productsWithoutVariants = computed(() => {
  const productIdsWithVariants = new Set(variants.value.map((variant) => variant.product));
  return products.value.filter((product) => !productIdsWithVariants.has(product.id));
});

function getProductName(productId: number): string {
  return (
    products.value.find((product) => product.id === productId)?.name ??
    `Sản phẩm #${String(productId)}`
  );
}

// Adjustment Modal State
const showAdjustModal = ref(false);
const adjustLoading = ref(false);
const selectedVariant = ref<AdminVariant | null>(null);
const adjustDelta = ref<number>(10);
const adjustKind = ref<"receipt" | "adjustment">("receipt");
const adjustReason = ref<string>("");

// Stock Movement History State
const showHistoryModal = ref(false);
const historyLoading = ref(false);
const historyMovements = ref<StockMovementItem[]>([]);
const historyVariant = ref<AdminVariant | null>(null);

async function loadVariants() {
  loading.value = true;
  error.value = "";
  try {
    if (isAdmin.value) {
      const [variantItems, productItems] = await Promise.all([
        fetchAdminVariants(),
        fetchAdminProducts(),
      ]);
      variants.value = variantItems;
      products.value = productItems;
    } else {
      variants.value = await fetchAdminVariants();
      products.value = [];
    }
  } catch (err) {
    error.value = toAppError(err).message;
  } finally {
    loading.value = false;
  }
}

function openAdjustModal(variant: AdminVariant) {
  selectedVariant.value = variant;
  adjustDelta.value = 10;
  adjustKind.value = "receipt";
  adjustReason.value = "";
  showAdjustModal.value = true;
}

async function handleAdjustSubmit() {
  if (!selectedVariant.value) return;
  if (!adjustReason.value.trim()) {
    toast.show("Vui lòng nhập lý do điều chỉnh.", "error");
    return;
  }
  if (adjustDelta.value === 0) {
    toast.show("Số lượng điều chỉnh phải khác 0.", "error");
    return;
  }

  adjustLoading.value = true;
  try {
    const movement = await adjustVariantInventory(selectedVariant.value.id, {
      delta: adjustDelta.value,
      kind: adjustKind.value,
      reason: adjustReason.value.trim(),
    });

    toast.show(
      `Đã cập nhật tồn kho thành công: ${String(movement.quantity_before)} ➔ ${String(movement.quantity_after)} đơn vị.`,
      "success",
    );

    // Update local variant quantity
    selectedVariant.value.inventory_quantity = movement.quantity_after;
    showAdjustModal.value = false;
  } catch (err) {
    toast.show(toAppError(err).message, "error");
  } finally {
    adjustLoading.value = false;
  }
}

async function openHistoryModal(variant: AdminVariant) {
  historyVariant.value = variant;
  showHistoryModal.value = true;
  historyLoading.value = true;
  try {
    historyMovements.value = await fetchVariantStockMovements(variant.id);
  } catch (err) {
    toast.show(toAppError(err).message, "error");
  } finally {
    historyLoading.value = false;
  }
}

function formatDate(dateStr: string) {
  return new Date(dateStr).toLocaleString("vi-VN", {
    year: "numeric",
    month: "2-digit",
    day: "2-digit",
    hour: "2-digit",
    minute: "2-digit",
  });
}

onMounted(loadVariants);
</script>

<template>
  <AdminLayout>
    <div class="space-y-6">
      <!-- Page Header -->
      <div class="flex flex-wrap items-center justify-between gap-4 border-b border-white/10 pb-5">
        <div>
          <p class="text-xs font-bold uppercase tracking-widest text-emerald-400">
            Kho Vận Hàng Hóa
          </p>
          <h1 class="text-2xl sm:text-3xl font-black uppercase tracking-tight text-white mt-1">
            Quản Lý Kho Hàng & Tồn Kho
          </h1>
          <p class="text-sm text-slate-400 mt-1">
            Theo dõi số lượng tồn thực tế theo SKU, thực hiện nhập kho / điều chỉnh và kiểm tra nhật
            ký di biến động bất biến.
          </p>
        </div>
        <div class="flex items-center gap-3">
          <BaseButton
            size="sm"
            variant="ghost"
            class="rounded-xl border border-white/15 text-slate-300 hover:text-white"
            @click="loadVariants"
          >
            Làm mới danh sách
          </BaseButton>
        </div>
      </div>

      <AppAlert v-if="error" variant="error" title="Lỗi tải tồn kho">{{ error }}</AppAlert>

      <section
        v-if="!loading && isAdmin && productsWithoutVariants.length"
        class="rounded-2xl border border-amber-400/25 bg-amber-400/10 p-5"
        aria-labelledby="products-without-sku-title"
      >
        <div class="flex flex-col gap-4 lg:flex-row lg:items-center lg:justify-between">
          <div>
            <p class="text-xs font-black tracking-wider text-amber-300 uppercase">
              Cần thiết lập SKU
            </p>
            <h2 id="products-without-sku-title" class="mt-1 text-base font-black text-white">
              {{ productsWithoutVariants.length }} sản phẩm chưa thể nhập kho
            </h2>
            <p class="mt-1 max-w-2xl text-sm text-slate-300">
              Tồn kho được quản lý theo biến thể SKU, không quản lý trực tiếp trên sản phẩm. Hãy tạo
              ít nhất một SKU rồi quay lại điều chỉnh số lượng.
            </p>
          </div>
          <div class="flex flex-wrap gap-2">
            <AppLink
              v-for="product in productsWithoutVariants.slice(0, 3)"
              :key="product.id"
              :to="`/admin/variants?product=${String(product.id)}&create=1`"
              class="rounded-xl border border-amber-300/30 bg-amber-300/10 px-3 py-2 text-xs font-bold text-amber-200 no-underline hover:bg-amber-300/20"
            >
              Tạo SKU · {{ product.name }}
            </AppLink>
          </div>
        </div>
      </section>

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
        <span class="text-sm font-semibold">Đang tải danh sách biến thể và kho hàng…</span>
      </div>

      <!-- Empty State -->
      <div
        v-else-if="variants.length === 0"
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
              d="M20 7l-8-4-8 4m16 0l-8 4m8-4v10l-8 4m0-10L4 7m8 4v10M4 7v10l8 4"
            />
          </svg>
        </div>
        <h3 class="text-lg font-bold text-white">Chưa có biến thể SKU nào trong hệ thống</h3>
        <p class="mt-1 text-sm text-slate-400 max-w-md mx-auto">
          Sản phẩm chỉ xuất hiện trong kho sau khi có ít nhất một biến thể SKU.
        </p>
        <AppLink
          v-if="isAdmin"
          to="/admin/variants?create=1"
          class="mt-4 inline-flex rounded-xl bg-emerald-500 px-4 py-2 text-xs font-black text-black no-underline"
        >
          Tạo biến thể SKU
        </AppLink>
      </div>

      <!-- Inventory Table -->
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
                <th class="px-6 py-4">Mã SKU</th>
                <th class="px-6 py-4">Sản phẩm</th>
                <th class="px-6 py-4">Giá Niêm Yết</th>
                <th class="px-6 py-4 text-center">Tồn Kho Hiện Tại</th>
                <th class="px-6 py-4">Ngưỡng Báo Động</th>
                <th class="px-6 py-4 text-right">Thao Tác Kho</th>
              </tr>
            </thead>
            <tbody class="divide-y divide-white/5">
              <tr v-for="v in variants" :key="v.id" class="transition-colors hover:bg-white/[0.02]">
                <td class="px-6 py-4">
                  <span class="font-mono text-xs sm:text-sm font-bold text-emerald-400">
                    {{ v.sku }}
                  </span>
                </td>
                <td class="px-6 py-4 text-xs text-slate-400">
                  <span class="block font-semibold text-slate-300">{{
                    getProductName(v.product)
                  }}</span>
                  <span class="mt-0.5 block">ID #{{ v.product }}</span>
                </td>
                <td class="px-6 py-4 font-mono font-semibold text-white">
                  {{ Number(v.price).toLocaleString("vi-VN") }} ₫
                </td>
                <td class="px-6 py-4 text-center">
                  <span
                    :class="[
                      'inline-flex items-center gap-1.5 rounded-full px-3 py-1 font-mono text-xs font-black',
                      v.inventory_quantity > v.low_stock_threshold
                        ? 'border border-emerald-500/30 bg-emerald-500/15 text-emerald-400'
                        : v.inventory_quantity > 0
                          ? 'border border-amber-500/30 bg-amber-500/15 text-amber-400'
                          : 'border border-rose-500/30 bg-rose-500/15 text-rose-400',
                    ]"
                  >
                    {{ v.inventory_quantity }} đơn vị
                  </span>
                </td>
                <td class="px-6 py-4 text-xs text-slate-400 font-mono">
                  ≤ {{ v.low_stock_threshold }} đơn vị
                </td>
                <td class="px-6 py-4 text-right">
                  <div class="flex items-center justify-end gap-2">
                    <BaseButton
                      size="sm"
                      class="rounded-xl bg-emerald-500/20 text-emerald-400 border border-emerald-500/30 hover:bg-emerald-500/30 text-xs font-bold"
                      @click="openAdjustModal(v)"
                    >
                      Điều chỉnh tồn
                    </BaseButton>
                    <BaseButton
                      size="sm"
                      variant="ghost"
                      class="rounded-xl border border-white/10 text-slate-300 hover:text-white text-xs font-bold"
                      @click="openHistoryModal(v)"
                    >
                      Lịch sử
                    </BaseButton>
                  </div>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>

    <!-- Modal: Stock Adjustment -->
    <Teleport to="body">
      <div
        v-if="showAdjustModal"
        class="fixed inset-0 z-50 flex items-center justify-center p-4 sm:p-6"
        role="dialog"
      >
        <div class="fixed inset-0 bg-black/80 backdrop-blur-md" @click="showAdjustModal = false" />

        <div
          class="relative z-10 w-full max-w-lg overflow-hidden rounded-3xl border border-white/15 bg-[#12151e] p-6 sm:p-8 text-white shadow-[0_25px_70px_rgba(0,0,0,0.95)] space-y-5"
        >
          <div class="flex items-center justify-between border-b border-white/10 pb-4">
            <div>
              <h2 class="text-lg font-black uppercase tracking-tight">Điều Chỉnh Tồn Kho</h2>
              <p class="text-xs text-emerald-400 font-mono mt-0.5">
                SKU: {{ selectedVariant?.sku }}
              </p>
            </div>
            <button
              type="button"
              class="flex h-8 w-8 items-center justify-center rounded-full text-slate-400 hover:bg-white/10 hover:text-white"
              @click="showAdjustModal = false"
            >
              ✕
            </button>
          </div>

          <div class="space-y-4">
            <!-- Kind Selector -->
            <div>
              <label class="text-xs font-bold uppercase tracking-wider text-slate-300 block mb-2">
                Loại Giao Dịch
              </label>
              <div class="grid grid-cols-2 gap-3">
                <button
                  type="button"
                  :class="[
                    'h-11 rounded-xl font-black text-xs uppercase tracking-wider border cursor-pointer transition-all',
                    adjustKind === 'receipt'
                      ? 'border-emerald-400 bg-emerald-500/20 text-emerald-400'
                      : 'border-white/10 bg-white/5 text-slate-400',
                  ]"
                  @click="adjustKind = 'receipt'"
                >
                  Nhập kho (Receipt)
                </button>
                <button
                  type="button"
                  :class="[
                    'h-11 rounded-xl font-black text-xs uppercase tracking-wider border cursor-pointer transition-all',
                    adjustKind === 'adjustment'
                      ? 'border-amber-400 bg-amber-500/20 text-amber-400'
                      : 'border-white/10 bg-white/5 text-slate-400',
                  ]"
                  @click="adjustKind = 'adjustment'"
                >
                  Kiểm kê / Điều chỉnh
                </button>
              </div>
            </div>

            <!-- Delta Input -->
            <div>
              <label class="text-xs font-bold uppercase tracking-wider text-slate-300 block mb-1">
                Số lượng thay đổi (Delta)
              </label>
              <p class="text-[11px] text-slate-400 mb-2">
                Dương (+) để tăng tồn, âm (-) để giảm tồn. Không cho phép tồn âm.
              </p>
              <input
                id="adjust-delta"
                v-model.number="adjustDelta"
                type="number"
                placeholder="VD: 10 hoặc -5"
                class="w-full rounded-xl border border-white/15 bg-[#0b0e14] px-4 py-2.5 text-white font-mono font-bold focus:border-emerald-400 focus:outline-none"
              />
            </div>

            <!-- Reason Input -->
            <div>
              <label
                for="adjust-reason"
                class="text-xs font-bold uppercase tracking-wider text-slate-300 block mb-1"
              >
                Lý do thay đổi (Bắt buộc)
              </label>
              <input
                id="adjust-reason"
                v-model="adjustReason"
                type="text"
                placeholder="VD: Phiếu nhập NK-001 hoặc Kiểm kê định kỳ"
                class="w-full rounded-xl border border-white/15 bg-[#0b0e14] px-4 py-2.5 text-white text-sm focus:border-emerald-400 focus:outline-none"
              />
            </div>
          </div>

          <div class="flex items-center justify-end gap-3 pt-4 border-t border-white/10">
            <BaseButton
              type="button"
              variant="ghost"
              class="rounded-xl border border-white/15 text-slate-300 hover:bg-white/10"
              @click="showAdjustModal = false"
            >
              Hủy
            </BaseButton>
            <BaseButton
              type="button"
              class="rounded-xl min-h-11 px-6 font-black uppercase tracking-wider text-xs"
              :loading="adjustLoading"
              @click="handleAdjustSubmit"
            >
              Xác nhận thay đổi
            </BaseButton>
          </div>
        </div>
      </div>
    </Teleport>

    <!-- Modal: Stock Movements History -->
    <Teleport to="body">
      <div
        v-if="showHistoryModal"
        class="fixed inset-0 z-50 flex items-center justify-center p-4 sm:p-6"
        role="dialog"
      >
        <div class="fixed inset-0 bg-black/80 backdrop-blur-md" @click="showHistoryModal = false" />

        <div
          class="relative z-10 w-full max-w-2xl max-h-[85vh] flex flex-col overflow-hidden rounded-3xl border border-white/15 bg-[#12151e] p-6 text-white shadow-[0_25px_70px_rgba(0,0,0,0.95)]"
        >
          <div class="flex items-center justify-between border-b border-white/10 pb-4">
            <div>
              <h2 class="text-lg font-black uppercase tracking-tight">Lịch Sử Biến Động Kho</h2>
              <p class="text-xs text-emerald-400 font-mono mt-0.5">
                SKU: {{ historyVariant?.sku }}
              </p>
            </div>
            <button
              type="button"
              class="flex h-8 w-8 items-center justify-center rounded-full text-slate-400 hover:bg-white/10 hover:text-white"
              @click="showHistoryModal = false"
            >
              ✕
            </button>
          </div>

          <!-- History Content -->
          <div class="flex-1 overflow-y-auto py-4 space-y-3">
            <div v-if="historyLoading" class="p-8 text-center text-slate-400">
              <svg
                class="mx-auto h-6 w-6 animate-spin text-emerald-400 mb-2"
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
              <span class="text-xs font-semibold">Đang tải lịch sử…</span>
            </div>

            <div v-else-if="historyMovements.length === 0" class="p-8 text-center text-slate-400">
              Chưa có biến động kho nào được ghi nhận cho biến thể này.
            </div>

            <div
              v-else
              v-for="m in historyMovements"
              :key="m.id"
              class="rounded-2xl border border-white/10 bg-white/5 p-4 space-y-2 text-xs"
            >
              <div class="flex items-center justify-between">
                <span
                  :class="[
                    'font-mono font-black rounded px-2 py-0.5',
                    m.delta > 0
                      ? 'bg-emerald-500/20 text-emerald-400'
                      : 'bg-rose-500/20 text-rose-400',
                  ]"
                >
                  {{ m.delta > 0 ? "+" + m.delta : m.delta }} đơn vị ({{
                    m.kind === "receipt" ? "Nhập kho" : "Điều chỉnh"
                  }})
                </span>
                <span class="text-slate-400">{{ formatDate(m.created_at) }}</span>
              </div>
              <div class="flex items-center justify-between text-slate-300">
                <span
                  >Tồn trước:
                  <strong class="font-mono text-white">{{ m.quantity_before }}</strong> ➔ Tồn sau:
                  <strong class="font-mono text-emerald-400">{{ m.quantity_after }}</strong></span
                >
                <span v-if="m.actor_email" class="text-slate-400">Bởi: {{ m.actor_email }}</span>
              </div>
              <p class="text-slate-300 italic">"{{ m.reason }}"</p>
            </div>
          </div>

          <div class="pt-4 border-t border-white/10 flex justify-end">
            <BaseButton
              type="button"
              variant="ghost"
              class="rounded-xl border border-white/15 text-slate-300 hover:bg-white/10 text-xs font-bold"
              @click="showHistoryModal = false"
            >
              Đóng
            </BaseButton>
          </div>
        </div>
      </div>
    </Teleport>
  </AdminLayout>
</template>
