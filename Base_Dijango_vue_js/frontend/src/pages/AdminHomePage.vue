<script setup lang="ts">
import { computed, onMounted, ref } from "vue";

import AppAlert from "@/components/feedback/AppAlert.vue";
import AppLink from "@/components/navigation/AppLink.vue";
import AdminLayout from "@/layouts/AdminLayout.vue";
import { toAppError } from "@/lib/http/errors";
import { verifyAdminAccessRequest } from "@/modules/admin/api";
import {
  ADMIN_METRICS,
  ORDER_QUEUE,
  RECENT_ACTIVITY,
  STAFF_METRICS,
  WEEKLY_REVENUE,
} from "@/modules/admin/dashboard.mock";
import { useAuth } from "@/modules/auth/composables/useAuth";

const { user } = useAuth();
const accessError = ref("");
const accessLoading = ref(true);

const isAdmin = computed(() => user.value?.roles.includes("ADMIN") ?? false);
const metrics = computed(() => (isAdmin.value ? ADMIN_METRICS : STAFF_METRICS));
const firstName = computed(() =>
  (user.value?.full_name || user.value?.email || "bạn").split(" ").at(-1),
);
const revenueChartPoints = computed(() =>
  WEEKLY_REVENUE.map((day, index) => ({
    ...day,
    x: 48 + index * (604 / Math.max(WEEKLY_REVENUE.length - 1, 1)),
    y: 180 - day.value * 1.4,
  })),
);
const revenuePolyline = computed(() =>
  revenueChartPoints.value.map((point) => `${String(point.x)},${String(point.y)}`).join(" "),
);

onMounted(async () => {
  try {
    await verifyAdminAccessRequest();
  } catch (error) {
    accessError.value = toAppError(error).message;
  } finally {
    accessLoading.value = false;
  }
});
</script>

<template>
  <AdminLayout>
    <div class="space-y-7">
      <header class="flex flex-col gap-4 sm:flex-row sm:items-end sm:justify-between">
        <div>
          <div class="flex flex-wrap items-center gap-2">
            <p class="text-xs font-black tracking-[0.18em] text-emerald-400 uppercase">
              {{ isAdmin ? "Tổng quan kinh doanh" : "Bảng công việc trong ca" }}
            </p>
            <span
              class="rounded-full border border-amber-400/25 bg-amber-400/10 px-2 py-1 text-[10px] font-bold text-amber-300"
              >Dữ liệu minh họa</span
            >
          </div>
          <h1 class="mt-2 text-2xl font-black tracking-tight text-white sm:text-3xl">
            Chào {{ firstName }}, hôm nay cần làm gì?
          </h1>
          <p class="mt-2 max-w-2xl text-sm leading-6 text-slate-400">
            {{
              isAdmin
                ? "Theo dõi nhanh sức khỏe cửa hàng và đi thẳng tới khu vực cần xử lý."
                : "Ưu tiên đơn mới, đơn đang chuẩn bị và các SKU sắp hết trong ca làm việc."
            }}
          </p>
        </div>
        <p class="text-xs font-semibold text-slate-500">Cập nhật giả lập: 10:45 · 18/09/2026</p>
      </header>

      <AppAlert v-if="accessError" variant="error" title="Không thể xác minh quyền">{{
        accessError
      }}</AppAlert>
      <div v-else-if="accessLoading" class="h-1 overflow-hidden rounded-full bg-white/5">
        <div class="h-full w-1/3 animate-pulse rounded-full bg-emerald-500" />
      </div>

      <section class="grid gap-4 sm:grid-cols-2 xl:grid-cols-4" aria-label="Chỉ số tổng quan">
        <article
          v-for="metric in metrics"
          :key="metric.label"
          class="rounded-2xl border border-white/10 bg-[#12151e] p-5 shadow-[0_18px_45px_-30px_rgba(0,0,0,0.9)]"
        >
          <div class="flex items-start justify-between gap-3">
            <p class="text-xs font-bold tracking-wider text-slate-400 uppercase">
              {{ metric.label }}
            </p>
            <span
              :class="[
                'rounded-full px-2 py-1 text-[10px] font-black',
                metric.trend === 'up'
                  ? 'bg-emerald-500/15 text-emerald-400'
                  : metric.trend === 'down'
                    ? 'bg-amber-400/15 text-amber-300'
                    : 'bg-sky-400/15 text-sky-300',
              ]"
              >{{ metric.change }}</span
            >
          </div>
          <p class="mt-5 text-3xl font-black tracking-tight text-white">{{ metric.value }}</p>
          <p class="mt-1 text-xs text-slate-500">{{ metric.helper }}</p>
        </article>
      </section>

      <div class="grid gap-6 xl:grid-cols-[minmax(0,1.3fr)_minmax(22rem,0.7fr)]">
        <section class="rounded-2xl border border-white/10 bg-[#12151e] p-5 sm:p-6">
          <div class="flex items-center justify-between gap-3">
            <div>
              <p class="text-xs font-black tracking-wider text-emerald-400 uppercase">
                Luồng đơn hàng
              </p>
              <h2 class="mt-1 text-lg font-black text-white">Hàng đợi cần xử lý</h2>
            </div>
            <AppLink
              to="/admin/orders"
              class="rounded-xl border border-white/10 bg-white/5 px-3 py-2 text-xs text-slate-300 no-underline hover:text-white"
              >Mở đơn hàng</AppLink
            >
          </div>
          <div class="mt-5 grid gap-3 sm:grid-cols-2">
            <AppLink
              v-for="queue in ORDER_QUEUE"
              :key="queue.label"
              :to="{ path: '/admin/orders' }"
              class="group flex items-center justify-between gap-4 rounded-xl border border-white/8 bg-white/[0.025] p-4 no-underline hover:border-white/20 hover:bg-white/[0.045]"
            >
              <div>
                <p class="text-sm font-bold text-white">{{ queue.label }}</p>
                <p class="mt-1 text-xs leading-5 text-slate-500">{{ queue.helper }}</p>
              </div>
              <span
                :class="[
                  'grid h-11 w-11 shrink-0 place-items-center rounded-xl text-lg font-black',
                  queue.tone === 'amber'
                    ? 'bg-amber-400/15 text-amber-300'
                    : queue.tone === 'sky'
                      ? 'bg-sky-400/15 text-sky-300'
                      : queue.tone === 'violet'
                        ? 'bg-violet-400/15 text-violet-300'
                        : 'bg-emerald-500/15 text-emerald-400',
                ]"
                >{{ queue.count }}</span
              >
            </AppLink>
          </div>
        </section>

        <section class="rounded-2xl border border-white/10 bg-[#12151e] p-5 sm:p-6">
          <p class="text-xs font-black tracking-wider text-emerald-400 uppercase">Thao tác nhanh</p>
          <h2 class="mt-1 text-lg font-black text-white">Đi thẳng tới công việc</h2>
          <div class="mt-5 space-y-3">
            <AppLink
              to="/admin/orders"
              class="flex items-center justify-between rounded-xl border border-white/10 bg-white/[0.025] p-4 text-sm text-white no-underline hover:border-emerald-500/30 hover:bg-emerald-500/8"
              ><span
                ><strong class="block">Xử lý đơn mới</strong
                ><small class="mt-1 block text-slate-500"
                  >Xác nhận và chuyển trạng thái</small
                ></span
              ><span aria-hidden="true">→</span></AppLink
            >
            <AppLink
              to="/admin/inventory"
              class="flex items-center justify-between rounded-xl border border-white/10 bg-white/[0.025] p-4 text-sm text-white no-underline hover:border-emerald-500/30 hover:bg-emerald-500/8"
              ><span
                ><strong class="block">Kiểm tra tồn kho</strong
                ><small class="mt-1 block text-slate-500"
                  >Nhập hàng hoặc điều chỉnh SKU</small
                ></span
              ><span aria-hidden="true">→</span></AppLink
            >
            <AppLink
              v-if="isAdmin"
              to="/admin/products"
              class="flex items-center justify-between rounded-xl border border-white/10 bg-white/[0.025] p-4 text-sm text-white no-underline hover:border-emerald-500/30 hover:bg-emerald-500/8"
              ><span
                ><strong class="block">Thêm sản phẩm</strong
                ><small class="mt-1 block text-slate-500">Tạo nội dung và ảnh bán hàng</small></span
              ><span aria-hidden="true">→</span></AppLink
            >
          </div>
        </section>
      </div>

      <div class="grid gap-6 xl:grid-cols-[minmax(0,1fr)_24rem]">
        <section v-if="isAdmin" class="rounded-2xl border border-white/10 bg-[#12151e] p-5 sm:p-6">
          <div class="flex items-end justify-between gap-3">
            <div>
              <p class="text-xs font-black tracking-wider text-emerald-400 uppercase">
                7 ngày gần nhất
              </p>
              <h2 class="mt-1 text-lg font-black text-white">Xu hướng doanh thu</h2>
            </div>
            <p class="text-xs text-slate-500">Đơn vị tương đối · mock</p>
          </div>
          <div class="mt-5 overflow-hidden" role="img" aria-label="Biểu đồ đường doanh thu 7 ngày">
            <svg class="h-56 w-full" viewBox="0 0 700 220" preserveAspectRatio="none">
              <line
                v-for="y in [40, 75, 110, 145, 180]"
                :key="y"
                x1="48"
                :y1="y"
                x2="652"
                :y2="y"
                class="stroke-slate-500/20"
                stroke-dasharray="4 6"
              />
              <polyline
                :points="revenuePolyline"
                fill="none"
                class="stroke-emerald-500"
                stroke-width="4"
                stroke-linecap="round"
                stroke-linejoin="round"
                vector-effect="non-scaling-stroke"
              />
              <g v-for="point in revenueChartPoints" :key="point.label">
                <circle
                  :cx="point.x"
                  :cy="point.y"
                  r="6"
                  class="fill-white stroke-emerald-500"
                  stroke-width="4"
                  vector-effect="non-scaling-stroke"
                />
                <text
                  :x="point.x"
                  :y="point.y - 14"
                  text-anchor="middle"
                  class="fill-slate-500 text-[11px] font-bold"
                >
                  {{ point.value }}
                </text>
                <text
                  :x="point.x"
                  y="210"
                  text-anchor="middle"
                  class="fill-slate-400 text-[11px] font-bold"
                >
                  {{ point.label }}
                </text>
              </g>
            </svg>
          </div>
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
          <h2 class="mt-1 text-lg font-black text-white">Nhật ký vận hành</h2>
          <ol class="mt-5 space-y-4">
            <li
              v-for="activity in RECENT_ACTIVITY"
              :key="`${activity.time}-${activity.title}`"
              class="grid grid-cols-[2.75rem_1fr] gap-3"
            >
              <span class="pt-0.5 text-xs font-black text-emerald-400">{{ activity.time }}</span>
              <div class="border-l border-white/10 pl-3">
                <p class="text-sm font-semibold leading-5 text-slate-200">{{ activity.title }}</p>
                <p class="mt-1 text-xs text-slate-500">{{ activity.actor }}</p>
              </div>
            </li>
          </ol>
        </section>
      </div>
    </div>
  </AdminLayout>
</template>
