<script setup lang="ts">
import { computed, onMounted, ref } from "vue";

import BaseButton from "@/components/base/BaseButton.vue";
import BaseInput from "@/components/base/BaseInput.vue";
import AppAlert from "@/components/feedback/AppAlert.vue";
import FormField from "@/components/form/FormField.vue";
import AdminLayout from "@/layouts/AdminLayout.vue";
import { toAppError } from "@/lib/http/errors";
import { useAuth } from "@/modules/auth/composables/useAuth";
import {
  downloadConsolidatedReport,
  fetchInventoryReport,
  fetchRecommendationReport,
  fetchReturnsReport,
  fetchSalesReport,
  type InventoryReport,
  type RecommendationReport,
  type ReportParams,
  type ReturnsReport,
  type SalesReport,
} from "../api";

type ReportTab = "sales" | "inventory" | "returns" | "recommendations";

const { user } = useAuth();
const isAdmin = computed(() => user.value?.roles.includes("ADMIN") ?? false);
const today = new Date();
const start = new Date(today);
start.setDate(today.getDate() - 29);
const startDate = ref(start.toISOString().slice(0, 10));
const endDate = ref(today.toISOString().slice(0, 10));
const activeTab = ref<ReportTab>(isAdmin.value ? "sales" : "inventory");
const sales = ref<SalesReport | null>(null);
const inventory = ref<InventoryReport | null>(null);
const returns = ref<ReturnsReport | null>(null);
const recommendations = ref<RecommendationReport | null>(null);
const loading = ref(false);
const exporting = ref(false);
const errorMessage = ref("");

const tabs = computed(() => [
  ...(isAdmin.value ? [{ key: "sales" as const, label: "Doanh thu" }] : []),
  { key: "inventory" as const, label: "Tồn kho" },
  { key: "returns" as const, label: "Đổi hàng" },
  { key: "recommendations" as const, label: "Gợi ý sản phẩm" },
]);

const params = computed<ReportParams>(() => ({
  start_date: startDate.value,
  end_date: endDate.value,
  timezone: "Asia/Ho_Chi_Minh",
}));

function formatMoney(value: string): string {
  return `${new Intl.NumberFormat("vi-VN").format(Number(value))} ₫`;
}

async function loadReport(): Promise<void> {
  loading.value = true;
  errorMessage.value = "";
  try {
    if (activeTab.value === "sales") sales.value = await fetchSalesReport(params.value);
    if (activeTab.value === "inventory") {
      inventory.value = await fetchInventoryReport(params.value);
    }
    if (activeTab.value === "returns") returns.value = await fetchReturnsReport(params.value);
    if (activeTab.value === "recommendations") {
      recommendations.value = await fetchRecommendationReport(params.value);
    }
  } catch (error) {
    errorMessage.value = toAppError(error).message;
  } finally {
    loading.value = false;
  }
}

async function selectTab(tab: ReportTab): Promise<void> {
  activeTab.value = tab;
  await loadReport();
}

async function exportExcel(): Promise<void> {
  exporting.value = true;
  errorMessage.value = "";
  try {
    const blob = await downloadConsolidatedReport(params.value);
    const url = URL.createObjectURL(blob);
    const anchor = globalThis.document.createElement("a");
    anchor.href = url;
    anchor.download = `bao-cao-tong-hop-${startDate.value}-${endDate.value}.xlsx`;
    anchor.click();
    URL.revokeObjectURL(url);
  } catch (error) {
    errorMessage.value = toAppError(error).message;
  } finally {
    exporting.value = false;
  }
}

onMounted(loadReport);
</script>

<template>
  <AdminLayout>
    <div class="space-y-6">
      <header>
        <p class="text-xs font-black tracking-[0.18em] text-emerald-400 uppercase">Phase 8</p>
        <h1 class="mt-2 text-3xl font-black text-white">Báo cáo vận hành</h1>
        <p class="mt-2 text-sm text-slate-400">
          Theo dõi doanh thu, giá vốn, lợi nhuận và tải một file Excel tổng hợp nhiều sheet.
        </p>
      </header>

      <section class="rounded-2xl border border-white/10 bg-[#12151e] p-4 sm:p-5">
        <div
          class="grid gap-4 sm:grid-cols-2 xl:grid-cols-[12rem_12rem_1fr_auto_auto] xl:items-end"
        >
          <FormField v-slot="field" label="Từ ngày" name="report-start-date">
            <BaseInput
              v-model="startDate"
              :id="field.id"
              name="start_date"
              type="date"
              :invalid="field.invalid"
              :aria-describedby="field.describedBy"
            />
          </FormField>
          <FormField v-slot="field" label="Đến ngày" name="report-end-date">
            <BaseInput
              v-model="endDate"
              :id="field.id"
              name="end_date"
              type="date"
              :invalid="field.invalid"
              :aria-describedby="field.describedBy"
            />
          </FormField>
          <div class="flex flex-wrap gap-2">
            <BaseButton
              v-for="tab in tabs"
              :key="tab.key"
              size="sm"
              :variant="activeTab === tab.key ? 'primary' : 'secondary'"
              @click="selectTab(tab.key)"
            >
              {{ tab.label }}
            </BaseButton>
          </div>
          <BaseButton variant="secondary" :loading="loading" @click="loadReport">
            Áp dụng
          </BaseButton>
          <BaseButton :loading="exporting" @click="exportExcel">Xuất Excel tổng hợp</BaseButton>
        </div>
      </section>

      <AppAlert v-if="errorMessage" variant="error" title="Không tải được báo cáo">
        {{ errorMessage }}
      </AppAlert>
      <div v-if="loading" class="h-2 animate-pulse rounded-full bg-emerald-500/20" />

      <template v-if="activeTab === 'sales' && sales">
        <section class="grid gap-4 sm:grid-cols-2 xl:grid-cols-3">
          <article
            v-for="item in [
              ['Doanh thu thuần', formatMoney(sales.summary.net_revenue)],
              ['Giá vốn', formatMoney(sales.summary.cost_of_goods_sold)],
              ['Lợi nhuận', formatMoney(sales.summary.profit)],
              ['Đơn đã trả', sales.summary.paid_orders],
              ['Giá trị đơn TB', formatMoney(sales.summary.average_order_value)],
              ['Tỷ lệ hủy', `${sales.summary.cancellation_rate_percent}%`],
            ]"
            :key="item[0]"
            class="rounded-2xl border border-white/10 bg-[#12151e] p-5"
          >
            <p class="text-xs font-bold text-slate-500 uppercase">{{ item[0] }}</p>
            <p class="mt-3 text-2xl font-black text-white">{{ item[1] }}</p>
          </article>
        </section>
        <section class="rounded-2xl border border-white/10 bg-[#12151e] p-5">
          <h2 class="text-lg font-black text-white">Sản phẩm bán chạy</h2>
          <div class="mt-4 overflow-x-auto">
            <table class="w-full text-left text-sm">
              <thead class="text-xs text-slate-500 uppercase">
                <tr>
                  <th class="py-3">Sản phẩm</th>
                  <th>Số lượng</th>
                  <th>Doanh thu thuần</th>
                </tr>
              </thead>
              <tbody>
                <tr
                  v-for="row in sales.best_sellers"
                  :key="row.product_id"
                  class="border-t border-white/8"
                >
                  <td class="py-3 font-semibold text-white">{{ row.product_name }}</td>
                  <td>{{ row.quantity }}</td>
                  <td>{{ formatMoney(row.net_revenue) }}</td>
                </tr>
              </tbody>
            </table>
            <p v-if="!sales.best_sellers.length" class="py-8 text-center text-slate-500">
              Chưa có đơn đã thanh toán trong kỳ.
            </p>
          </div>
        </section>
        <section class="rounded-2xl border border-white/10 bg-[#12151e] p-5">
          <h2 class="text-lg font-black text-white">Lý do hủy đơn</h2>
          <div class="mt-4 grid gap-3 sm:grid-cols-2 xl:grid-cols-3">
            <article
              v-for="row in sales.cancellation_reasons"
              :key="row.reason"
              class="rounded-xl bg-white/5 p-4"
            >
              <p class="text-sm text-slate-300">{{ row.reason }}</p>
              <p class="mt-2 text-xl font-black text-rose-400">{{ row.count }}</p>
            </article>
          </div>
          <p v-if="!sales.cancellation_reasons.length" class="mt-4 text-sm text-slate-500">
            Không có đơn bị hủy trong kỳ.
          </p>
        </section>
      </template>

      <template v-if="activeTab === 'inventory' && inventory">
        <section class="grid gap-4 sm:grid-cols-3">
          <article
            v-for="item in [
              ['SKU hoạt động', inventory.summary.active_skus],
              ['SKU sắp hết', inventory.summary.low_stock_skus],
              ['Tổng đơn vị tồn', inventory.summary.units_on_hand],
            ]"
            :key="item[0]"
            class="rounded-2xl border border-white/10 bg-[#12151e] p-5"
          >
            <p class="text-xs font-bold text-slate-500 uppercase">{{ item[0] }}</p>
            <p class="mt-3 text-2xl font-black text-white">{{ item[1] }}</p>
          </article>
        </section>
        <section class="rounded-2xl border border-white/10 bg-[#12151e] p-5">
          <h2 class="text-lg font-black text-white">Danh sách tồn thấp</h2>
          <div class="mt-4 overflow-x-auto">
            <table class="w-full text-left text-sm">
              <thead class="text-xs text-slate-500 uppercase">
                <tr>
                  <th class="py-3">SKU</th>
                  <th>Sản phẩm</th>
                  <th>Tồn</th>
                  <th>Ngưỡng</th>
                </tr>
              </thead>
              <tbody>
                <tr
                  v-for="row in inventory.low_stock"
                  :key="row.variant_id"
                  class="border-t border-white/8"
                >
                  <td class="py-3 font-mono text-emerald-400">{{ row.sku }}</td>
                  <td>{{ row.product_name }}</td>
                  <td>{{ row.quantity }}</td>
                  <td>{{ row.threshold }}</td>
                </tr>
              </tbody>
            </table>
            <p v-if="!inventory.low_stock.length" class="py-8 text-center text-slate-500">
              Không có SKU dưới ngưỡng.
            </p>
          </div>
        </section>
        <section class="rounded-2xl border border-white/10 bg-[#12151e] p-5">
          <h2 class="text-lg font-black text-white">Tuổi tồn kho</h2>
          <div class="mt-4 overflow-x-auto">
            <table class="w-full text-left text-sm">
              <thead class="text-xs text-slate-500 uppercase">
                <tr>
                  <th class="py-3">SKU</th>
                  <th>Sản phẩm</th>
                  <th>Tồn</th>
                  <th>Số ngày</th>
                </tr>
              </thead>
              <tbody>
                <tr
                  v-for="row in inventory.ageing.slice(0, 20)"
                  :key="row.variant_id"
                  class="border-t border-white/8"
                >
                  <td class="py-3 font-mono text-emerald-400">{{ row.sku }}</td>
                  <td>{{ row.product_name }}</td>
                  <td>{{ row.quantity }}</td>
                  <td>{{ row.age_days }}</td>
                </tr>
              </tbody>
            </table>
          </div>
          <div class="mt-5 flex flex-wrap gap-2">
            <span
              v-for="row in inventory.movement_summary"
              :key="row.kind"
              class="rounded-full bg-white/5 px-3 py-2 text-xs text-slate-300"
            >
              {{ row.kind }}: {{ row.movements }} lượt / {{ row.net_quantity }} đơn vị
            </span>
          </div>
        </section>
      </template>

      <template v-if="activeTab === 'returns' && returns">
        <section class="grid gap-4 sm:grid-cols-4">
          <article
            v-for="item in [
              ['Yêu cầu đổi', returns.summary.requests],
              ['Đã hoàn tất', returns.summary.completed],
              ['Tỷ lệ đổi', `${returns.summary.exchange_rate_percent}%`],
              ['Giờ xử lý TB', returns.summary.average_processing_hours],
            ]"
            :key="item[0]"
            class="rounded-2xl border border-white/10 bg-[#12151e] p-5"
          >
            <p class="text-xs font-bold text-slate-500 uppercase">{{ item[0] }}</p>
            <p class="mt-3 text-2xl font-black text-white">{{ item[1] }}</p>
          </article>
        </section>
        <section class="rounded-2xl border border-white/10 bg-[#12151e] p-5">
          <h2 class="text-lg font-black text-white">Theo trạng thái</h2>
          <div class="mt-4 grid gap-3 sm:grid-cols-3">
            <div
              v-for="row in returns.by_status"
              :key="row.status"
              class="rounded-xl bg-white/5 p-4"
            >
              <p class="text-xs text-slate-500 uppercase">{{ row.status }}</p>
              <p class="mt-2 text-xl font-black text-white">{{ row.count }}</p>
            </div>
          </div>
        </section>
      </template>

      <section
        v-if="activeTab === 'recommendations' && recommendations"
        class="rounded-2xl border border-white/10 bg-[#12151e] p-5"
      >
        <h2 class="text-lg font-black text-white">Hiệu quả theo chiến lược</h2>
        <div class="mt-4 overflow-x-auto">
          <table class="w-full text-left text-sm">
            <thead class="text-xs text-slate-500 uppercase">
              <tr>
                <th class="py-3">Chiến lược</th>
                <th>Request</th>
                <th>Impression</th>
                <th>CTR</th>
                <th>Thêm giỏ</th>
                <th>Mua</th>
                <th>Coverage</th>
              </tr>
            </thead>
            <tbody>
              <tr
                v-for="row in recommendations.strategies"
                :key="row.strategy"
                class="border-t border-white/8"
              >
                <td class="py-3 font-bold text-white">{{ row.strategy }}</td>
                <td>{{ row.requests }}</td>
                <td>{{ row.impressions }}</td>
                <td>{{ row.ctr_percent }}%</td>
                <td>{{ row.add_to_carts }}</td>
                <td>{{ row.purchases }}</td>
                <td>{{ row.coverage_percent }}%</td>
              </tr>
            </tbody>
          </table>
        </div>
      </section>
    </div>
  </AdminLayout>
</template>
