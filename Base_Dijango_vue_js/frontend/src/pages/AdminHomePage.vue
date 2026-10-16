<script setup lang="ts">
import { computed, onMounted, ref } from "vue";

import BaseButton from "@/components/base/BaseButton.vue";
import BaseInput from "@/components/base/BaseInput.vue";
import AppAlert from "@/components/feedback/AppAlert.vue";
import FormField from "@/components/form/FormField.vue";
import AppLink from "@/components/navigation/AppLink.vue";
import AdminLayout from "@/layouts/AdminLayout.vue";
import { toAppError } from "@/lib/http/errors";
import { useAuth } from "@/modules/auth/composables/useAuth";
import { fetchDashboard, type DashboardData } from "@/modules/operations/api";

const { user } = useAuth();
const dashboard = ref<DashboardData | null>(null);
const loading = ref(true);
const errorMessage = ref("");
const today = new Date();
const initialStart = new Date(today);
initialStart.setDate(today.getDate() - 6);
const startDate = ref(isoDate(initialStart));
const endDate = ref(isoDate(today));

const isAdmin = computed(() => user.value?.roles.includes("ADMIN") ?? false);
const firstName = computed(() =>
  (user.value?.full_name || user.value?.email || "bạn").split(" ").at(-1),
);

function isoDate(date: Date): string {
  return date.toISOString().slice(0, 10);
}

function reportParams() {
  return {
    start_date: startDate.value,
    end_date: endDate.value,
    timezone: "Asia/Ho_Chi_Minh",
  };
}

function formatMoney(value: string | number): string {
  return `${new Intl.NumberFormat("vi-VN").format(Number(value))} ₫`;
}

function statusLabel(status: string): string {
  return (
    {
      pending_confirmation: "Chờ xác nhận",
      confirmed: "Đã xác nhận",
      preparing: "Đang chuẩn bị",
      shipped: "Đang giao",
      delivered: "Đã giao",
      completed: "Hoàn tất",
      cancelled: "Đã hủy",
    }[status] ?? status
  );
}

const metrics = computed(() => {
  const data = dashboard.value;
  if (!data) return [];
  if (!isAdmin.value || !data.finance) {
    return [
      {
        label: "Chờ xác nhận",
        value: data.queue.pending_confirmation ?? 0,
        helper: "đơn cần xử lý",
      },
      { label: "Đang chuẩn bị", value: data.queue.preparing ?? 0, helper: "đơn trong kho" },
      { label: "Đang giao", value: data.queue.shipped ?? 0, helper: "đơn đang vận chuyển" },
      { label: "Đã giao", value: data.queue.delivered ?? 0, helper: "chờ khách xác nhận" },
      { label: "SKU sắp hết", value: data.low_stock_count, helper: "dưới ngưỡng an toàn" },
    ];
  }
  return [
    {
      label: "Doanh thu thuần",
      value: formatMoney(data.finance.net_revenue),
      helper:
        data.finance.revenue_change_percent === null
          ? "kỳ trước chưa có doanh thu"
          : `${Number(data.finance.revenue_change_percent) >= 0 ? "+" : ""}${data.finance.revenue_change_percent}% so với kỳ trước`,
    },
    {
      label: "Đơn đã thanh toán",
      value: data.finance.paid_order_count,
      helper: "trong kỳ hiện tại",
    },
    {
      label: "Lợi nhuận",
      value: formatMoney(data.finance.profit),
      helper: `Giá vốn ${formatMoney(data.finance.cost_of_goods_sold)}`,
    },
    { label: "SKU sắp hết", value: data.low_stock_count, helper: "cần bổ sung tồn" },
  ];
});

const chartPoints = computed(() => {
  const source = dashboard.value?.revenue_series ?? [];
  const max = Math.max(...source.map((item) => Number(item.revenue)), 1);
  return source.map((item, index) => ({
    ...item,
    x: 48 + index * (604 / Math.max(source.length - 1, 1)),
    y: 180 - (Number(item.revenue) / max) * 135,
  }));
});
const chartPolyline = computed(() =>
  chartPoints.value.map((point) => `${String(point.x)},${String(point.y)}`).join(" "),
);

async function loadDashboard(): Promise<void> {
  loading.value = true;
  errorMessage.value = "";
  try {
    dashboard.value = await fetchDashboard(reportParams());
  } catch (error) {
    errorMessage.value = toAppError(error).message;
  } finally {
    loading.value = false;
  }
}

onMounted(loadDashboard);
</script>

<template>
  <AdminLayout>
    <div class="space-y-7">
      <header class="flex flex-col gap-4 sm:flex-row sm:items-end sm:justify-between">
        <div>
          <p class="text-xs font-black tracking-[0.18em] text-emerald-400 uppercase">
            {{ isAdmin ? "Tổng quan kinh doanh" : "Bảng công việc trong ca" }}
          </p>
          <h1 class="mt-2 text-2xl font-black text-white sm:text-3xl">
            Chào {{ firstName }}, hôm nay cần làm gì?
          </h1>
          <p class="mt-2 text-sm text-slate-400">
            Dữ liệu thật được tổng hợp theo múi giờ Việt Nam và cập nhật từ hệ thống vận hành.
          </p>
        </div>
        <div class="grid grid-cols-2 gap-2 sm:flex sm:items-end">
          <FormField v-slot="field" label="Từ ngày" name="dashboard-start">
            <BaseInput
              v-model="startDate"
              :id="field.id"
              name="start_date"
              type="date"
              :invalid="field.invalid"
              :aria-describedby="field.describedBy"
            />
          </FormField>
          <FormField v-slot="field" label="Đến ngày" name="dashboard-end">
            <BaseInput
              v-model="endDate"
              :id="field.id"
              name="end_date"
              type="date"
              :invalid="field.invalid"
              :aria-describedby="field.describedBy"
            />
          </FormField>
          <BaseButton
            variant="secondary"
            size="sm"
            class="col-span-2"
            :loading="loading"
            @click="loadDashboard"
          >
            Áp dụng
          </BaseButton>
        </div>
      </header>

      <AppAlert v-if="errorMessage" variant="error" title="Không tải được dashboard">
        {{ errorMessage }}
      </AppAlert>

      <section v-if="loading && !dashboard" class="grid gap-4 sm:grid-cols-2 xl:grid-cols-4">
        <div v-for="index in 4" :key="index" class="h-32 animate-pulse rounded-2xl bg-white/5" />
      </section>
      <section
        v-else
        class="grid gap-4 sm:grid-cols-2 xl:grid-cols-4"
        aria-label="Chỉ số tổng quan"
      >
        <article
          v-for="metric in metrics"
          :key="metric.label"
          class="rounded-2xl border border-white/10 bg-[#12151e] p-5"
        >
          <p class="text-xs font-bold tracking-wider text-slate-400 uppercase">
            {{ metric.label }}
          </p>
          <p class="mt-5 text-3xl font-black text-white">{{ metric.value }}</p>
          <p class="mt-1 text-xs text-slate-500">{{ metric.helper }}</p>
        </article>
      </section>

      <div class="grid gap-6 xl:grid-cols-[minmax(0,1.3fr)_minmax(20rem,0.7fr)]">
        <section class="rounded-2xl border border-white/10 bg-[#12151e] p-5 sm:p-6">
          <div class="flex items-center justify-between">
            <div>
              <p class="text-xs font-black tracking-wider text-emerald-400 uppercase">
                Luồng đơn hàng
              </p>
              <h2 class="mt-1 text-lg font-black text-white">Hàng đợi cần xử lý</h2>
            </div>
            <AppLink to="/admin/orders" class="text-xs text-emerald-400">Mở đơn hàng →</AppLink>
          </div>
          <div class="mt-5 grid gap-3 sm:grid-cols-2">
            <article
              v-for="status in [
                'pending_confirmation',
                'preparing',
                'shipped',
                'delivered',
                'completed',
              ]"
              :key="status"
              class="flex items-center justify-between rounded-xl border border-white/8 bg-white/[0.025] p-4"
            >
              <p class="text-sm font-bold text-white">{{ statusLabel(status) }}</p>
              <span
                class="grid h-10 min-w-10 place-items-center rounded-xl bg-emerald-500/15 px-2 font-black text-emerald-400"
              >
                {{ dashboard?.queue[status] ?? 0 }}
              </span>
            </article>
          </div>
        </section>

        <section class="rounded-2xl border border-white/10 bg-[#12151e] p-5 sm:p-6">
          <p class="text-xs font-black tracking-wider text-emerald-400 uppercase">Thao tác nhanh</p>
          <div class="mt-5 space-y-3">
            <AppLink
              v-for="item in [
                { label: 'Xử lý đơn mới', to: '/admin/orders' },
                { label: 'Kiểm tra tồn kho', to: '/admin/inventory' },
                { label: 'Mở báo cáo', to: '/admin/reports' },
              ]"
              :key="item.to"
              :to="item.to"
              class="flex justify-between rounded-xl border border-white/10 p-4 text-sm font-bold text-white no-underline hover:border-emerald-500/30"
            >
              {{ item.label }} <span>→</span>
            </AppLink>
          </div>
        </section>
      </div>

      <div class="grid gap-6 xl:grid-cols-[minmax(0,1fr)_24rem]">
        <section v-if="isAdmin" class="rounded-2xl border border-white/10 bg-[#12151e] p-5 sm:p-6">
          <p class="text-xs font-black tracking-wider text-emerald-400 uppercase">
            7 ngày gần nhất
          </p>
          <h2 class="mt-1 text-lg font-black text-white">Xu hướng doanh thu thực tế</h2>
          <div
            v-if="chartPoints.length"
            class="mt-5 overflow-hidden"
            role="img"
            aria-label="Biểu đồ doanh thu"
          >
            <svg class="h-56 w-full" viewBox="0 0 700 220" preserveAspectRatio="none">
              <line
                v-for="y in [45, 90, 135, 180]"
                :key="y"
                x1="48"
                :y1="y"
                x2="652"
                :y2="y"
                class="stroke-slate-500/20"
                stroke-dasharray="4 6"
              />
              <polyline
                :points="chartPolyline"
                fill="none"
                class="stroke-emerald-500"
                stroke-width="4"
                vector-effect="non-scaling-stroke"
              />
              <g v-for="point in chartPoints" :key="point.date">
                <circle
                  :cx="point.x"
                  :cy="point.y"
                  r="5"
                  class="fill-white stroke-emerald-500"
                  stroke-width="3"
                />
                <text
                  :x="point.x"
                  y="210"
                  text-anchor="middle"
                  class="fill-slate-400 text-[11px] font-bold"
                >
                  {{ point.date.slice(5) }}
                </text>
              </g>
            </svg>
          </div>
          <p v-else class="mt-8 text-sm text-slate-500">Chưa có doanh thu trong kỳ này.</p>
        </section>

        <section
          :class="[
            'rounded-2xl border border-white/10 bg-[#12151e] p-5 sm:p-6',
            !isAdmin && 'xl:col-span-2',
          ]"
        >
          <p class="text-xs font-black tracking-wider text-emerald-400 uppercase">
            Hoạt động gần đây
          </p>
          <h2 class="mt-1 text-lg font-black text-white">Nhật ký đơn hàng</h2>
          <ol v-if="dashboard?.recent_activity.length" class="mt-5 space-y-4">
            <li
              v-for="activity in dashboard.recent_activity"
              :key="`${activity.order__number}-${activity.created_at}`"
              class="border-l border-white/10 pl-3"
            >
              <p class="text-sm font-semibold text-slate-200">
                {{ activity.order__number }} · {{ statusLabel(activity.to_status) }}
              </p>
              <p class="mt-1 text-xs text-slate-500">
                {{ activity.actor__email || "Hệ thống" }} ·
                {{ new Date(activity.created_at).toLocaleString("vi-VN") }}
              </p>
            </li>
          </ol>
          <p v-else class="mt-5 text-sm text-slate-500">Chưa có hoạt động.</p>
        </section>
      </div>
    </div>
  </AdminLayout>
</template>
