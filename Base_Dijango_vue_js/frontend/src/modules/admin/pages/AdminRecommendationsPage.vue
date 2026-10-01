<script setup lang="ts">
import { onMounted, ref } from "vue";

import BaseButton from "@/components/base/BaseButton.vue";
import AppAlert from "@/components/feedback/AppAlert.vue";
import AdminLayout from "@/layouts/AdminLayout.vue";
import { toAppError } from "@/lib/http/errors";
import { fetchRecommendationMetrics, type RecommendationMetrics } from "../api";

const metrics = ref<RecommendationMetrics | null>(null);
const loading = ref(true);
const error = ref("");

async function load(): Promise<void> {
  loading.value = true;
  error.value = "";
  try {
    metrics.value = await fetchRecommendationMetrics();
  } catch (err) {
    error.value = toAppError(err).message;
  } finally {
    loading.value = false;
  }
}

onMounted(() => void load());
</script>

<template>
  <AdminLayout>
    <div class="space-y-6">
      <header class="flex flex-wrap items-end justify-between gap-4 border-b border-white/10 pb-6">
        <div>
          <p class="text-xs font-black tracking-[0.2em] text-emerald-400 uppercase">Phase 7</p>
          <h1 class="mt-2 text-3xl font-black text-white">Hiệu quả gợi ý sản phẩm</h1>
          <p class="mt-2 text-sm text-slate-400">
            Số liệu 30 ngày gần nhất, phục vụ kiểm chứng recommendation.
          </p>
        </div>
        <BaseButton variant="secondary" :loading="loading" @click="load">Làm mới</BaseButton>
      </header>

      <AppAlert v-if="error" variant="error" title="Không tải được số liệu">{{ error }}</AppAlert>
      <div v-else-if="loading" class="grid gap-4 sm:grid-cols-2 xl:grid-cols-4">
        <div v-for="index in 4" :key="index" class="h-32 animate-pulse rounded-2xl bg-white/5" />
      </div>
      <template v-else-if="metrics">
        <section class="grid gap-4 sm:grid-cols-2 xl:grid-cols-4">
          <article
            v-for="item in [
              { label: 'Lượt hiển thị', value: metrics.impressions },
              { label: 'Lượt nhấp', value: metrics.clicks },
              { label: 'CTR', value: `${metrics.ctr_percent}%` },
              { label: 'Độ phủ catalog', value: `${metrics.coverage_percent}%` },
            ]"
            :key="item.label"
            class="rounded-2xl border border-white/10 bg-[#12151e] p-5"
          >
            <p class="text-xs font-bold tracking-wider text-slate-500 uppercase">
              {{ item.label }}
            </p>
            <p class="mt-3 text-3xl font-black text-white">{{ item.value }}</p>
          </article>
        </section>
        <section class="grid gap-4 lg:grid-cols-2">
          <article class="rounded-2xl border border-white/10 bg-[#12151e] p-6">
            <h2 class="font-black text-white">Chuyển đổi có attribution</h2>
            <div class="mt-5 grid grid-cols-2 gap-4">
              <div class="rounded-xl bg-white/5 p-4">
                <p class="text-xs text-slate-500">Thêm vào giỏ</p>
                <p class="mt-1 text-2xl font-black text-emerald-400">
                  {{ metrics.attributed_add_to_carts }}
                </p>
              </div>
              <div class="rounded-xl bg-white/5 p-4">
                <p class="text-xs text-slate-500">Mua hoàn tất</p>
                <p class="mt-1 text-2xl font-black text-emerald-400">
                  {{ metrics.attributed_purchases }}
                </p>
              </div>
            </div>
          </article>
          <article class="rounded-2xl border border-white/10 bg-[#12151e] p-6">
            <h2 class="font-black text-white">Request theo chiến lược</h2>
            <dl class="mt-4 space-y-3">
              <div
                v-for="(value, key) in metrics.requests_by_strategy"
                :key="key"
                class="flex justify-between rounded-xl bg-white/5 px-4 py-3 text-sm"
              >
                <dt class="font-bold text-slate-300">{{ key }}</dt>
                <dd class="font-mono font-black text-white">{{ value }}</dd>
              </div>
            </dl>
          </article>
        </section>
      </template>
    </div>
  </AdminLayout>
</template>
