<script setup lang="ts">
import { onMounted, ref, watch } from "vue";

import ProductCard from "./ProductCard.vue";
import {
  fetchPersonalizedRecommendations,
  fetchPopularRecommendations,
  fetchSimilarRecommendations,
  rememberRecommendationClick,
  sendProductEvent,
} from "../api";
import type { ProductListItem, RecommendationResponse } from "../types";

const props = withDefaults(
  defineProps<{
    mode: "popular" | "personalized" | "similar";
    productId?: number;
    eyebrow?: string;
    title: string;
    description?: string;
    limit?: number;
  }>(),
  { productId: undefined, eyebrow: "Gợi ý dành cho bạn", description: "", limit: 6 },
);

const products = ref<ProductListItem[]>([]);
const requestId = ref("");
const fallbackUsed = ref(false);
const loading = ref(true);

async function load(): Promise<void> {
  if (props.mode === "similar" && !props.productId) return;
  loading.value = true;
  try {
    let response: RecommendationResponse;
    if (props.mode === "similar") {
      const productId = props.productId;
      if (!productId) return;
      response = await fetchSimilarRecommendations(productId, props.limit);
    } else if (props.mode === "personalized") {
      response = await fetchPersonalizedRecommendations(props.limit);
    } else {
      response = await fetchPopularRecommendations(props.limit);
    }
    products.value = response.results;
    requestId.value = response.request_id;
    fallbackUsed.value = response.fallback_used;
    await Promise.all(
      response.results.map((product) =>
        sendProductEvent({
          event_type: "recommendation_impression",
          product: product.id,
          recommendation_context_id: response.request_id,
        }),
      ),
    );
  } catch {
    products.value = [];
  } finally {
    loading.value = false;
  }
}

function trackClick(productId: number): void {
  if (!requestId.value) return;
  rememberRecommendationClick(productId, requestId.value);
  void sendProductEvent({
    event_type: "recommendation_click",
    product: productId,
    recommendation_context_id: requestId.value,
  });
}

watch(
  () => props.productId,
  () => void load(),
);
onMounted(() => void load());
</script>

<template>
  <section v-if="loading || products.length" class="bg-[#090a0f] px-4 py-14 sm:px-6 lg:px-8">
    <div class="mx-auto max-w-7xl">
      <div class="flex flex-col justify-between gap-4 sm:flex-row sm:items-end">
        <div>
          <p class="text-xs font-black tracking-[0.18em] text-emerald-400 uppercase">
            {{ eyebrow }}
          </p>
          <h2 class="mt-2 text-2xl font-black text-white sm:text-3xl">{{ title }}</h2>
          <p v-if="description" class="mt-2 max-w-2xl text-sm text-slate-400">{{ description }}</p>
        </div>
        <span
          v-if="fallbackUsed"
          class="w-fit rounded-full border border-white/10 bg-white/5 px-3 py-1 text-xs font-bold text-slate-400"
          >Gợi ý phổ biến khi chưa đủ lịch sử</span
        >
      </div>
      <div v-if="loading" class="mt-7 grid grid-cols-2 gap-4 lg:grid-cols-4">
        <div
          v-for="index in 4"
          :key="index"
          class="aspect-[3/4] animate-pulse rounded-2xl bg-white/5"
        />
      </div>
      <div v-else class="mt-7 grid grid-cols-2 gap-4 md:grid-cols-3 lg:grid-cols-6">
        <ProductCard
          v-for="product in products"
          :key="product.id"
          :product="product"
          @select="trackClick"
        />
      </div>
    </div>
  </section>
</template>
