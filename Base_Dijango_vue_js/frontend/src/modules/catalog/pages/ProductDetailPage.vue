<script setup lang="ts">
import { computed, onMounted, ref, watch } from "vue";
import { useRoute, useRouter } from "vue-router";

import BaseButton from "@/components/base/BaseButton.vue";
import AppLink from "@/components/navigation/AppLink.vue";
import StorefrontLayout from "@/layouts/StorefrontLayout.vue";
import { useToastStore } from "@/app/stores/toast";
import { toAppError } from "@/lib/http/errors";
import { useCartStore } from "@/modules/cart/stores/cart";
import ReviewSection from "@/modules/engagement/components/ReviewSection.vue";
import RecommendationRail from "../components/RecommendationRail.vue";
import { useWishlistStore } from "@/modules/engagement/stores/wishlist";
import { useAuth } from "@/modules/auth/composables/useAuth";
import { fetchProductDetail, getRecommendationAttribution, sendProductEvent } from "../api";
import type { ProductDetail, ProductVariant } from "../types";

const route = useRoute();
const router = useRouter();
const toast = useToastStore();
const cartStore = useCartStore();
const wishlist = useWishlistStore();
const { isAuthenticated } = useAuth();

const loading = ref(true);
const error = ref("");
const product = ref<ProductDetail | null>(null);

const activeImageIndex = ref(0);
const selectedVariantId = ref<number | null>(null);
const selectedSizeId = ref<number | null>(null);
const selectedColorId = ref<number | null>(null);

const currentSlug = computed(() => (route.params.slug as string) || "");

function formatCurrency(amount: string | number | null | undefined): string {
  if (amount === null || amount === undefined || amount === "") return "Liên hệ";
  const num = typeof amount === "string" ? Number(amount) : amount;
  if (isNaN(num)) return "Liên hệ";
  return new Intl.NumberFormat("vi-VN", { style: "currency", currency: "VND" }).format(num);
}

const currentImage = computed<string>(() => {
  if (!product.value) return "";
  if (product.value.images.length > 0) {
    const img = product.value.images[activeImageIndex.value] || product.value.images[0];
    return img?.image_url || "";
  }
  return (
    product.value.primary_image?.image_url ||
    "https://images.unsplash.com/photo-1542291026-7eec264c27ff?auto=format&fit=crop&w=1000&q=80"
  );
});

const availableSizes = computed(() => {
  if (!product.value?.variants) return [];
  const map = new Map<number, { id: number; label: string; available: boolean }>();
  product.value.variants.forEach((v) => {
    if (v.size) {
      const existing = map.get(v.size.id);
      const isAvail = v.is_available;
      if (!existing) {
        map.set(v.size.id, { id: v.size.id, label: v.size.label, available: isAvail });
      } else if (isAvail) {
        existing.available = true;
      }
    }
  });
  return Array.from(map.values());
});

const availableColors = computed(() => {
  if (!product.value?.variants) return [];
  const map = new Map<number, { id: number; name: string; hex: string; available: boolean }>();
  product.value.variants.forEach((v) => {
    if (v.color) {
      const existing = map.get(v.color.id);
      const isAvail = v.is_available;
      if (!existing) {
        map.set(v.color.id, {
          id: v.color.id,
          name: v.color.name,
          hex: v.color.hex_code || "#10b981",
          available: isAvail,
        });
      } else if (isAvail) {
        existing.available = true;
      }
    }
  });
  return Array.from(map.values());
});

const matchedVariant = computed<ProductVariant | null>(() => {
  if (!product.value?.variants) return null;
  if (!selectedSizeId.value && !selectedColorId.value) return null;
  return (
    product.value.variants.find((v) => {
      const sizeMatch = !selectedSizeId.value || v.size?.id === selectedSizeId.value;
      const colorMatch = !selectedColorId.value || v.color?.id === selectedColorId.value;
      return sizeMatch && colorMatch;
    }) || null
  );
});

const displayPrice = computed(() => {
  if (!product.value) return "";
  if (matchedVariant.value) {
    return formatCurrency(matchedVariant.value.price);
  }
  if (
    product.value.min_price &&
    product.value.max_price &&
    product.value.min_price !== product.value.max_price
  ) {
    return `${formatCurrency(product.value.min_price)} - ${formatCurrency(product.value.max_price)}`;
  }
  return formatCurrency(product.value.min_price);
});

const currentStockStatus = computed(() => {
  if (matchedVariant.value) {
    return {
      available: matchedVariant.value.is_available,
      quantity: matchedVariant.value.inventory_quantity,
    };
  }
  return {
    available: product.value?.is_available ?? false,
    quantity: null,
  };
});

const defaultVariant = computed(() =>
  product.value?.variants.find((variant) => variant.is_available),
);

const unitLabel = computed(() => (product.value?.product_type === "footwear" ? "đôi" : "sản phẩm"));

async function loadProduct() {
  if (!currentSlug.value) return;
  loading.value = true;
  error.value = "";
  try {
    const data = await fetchProductDetail(currentSlug.value);
    product.value = data;

    // Preselect first available variant's size & color
    if (data.variants.length > 0) {
      const firstAvailable = data.variants.find((v) => v.is_available) || data.variants[0];
      if (firstAvailable) {
        selectedSizeId.value = firstAvailable.size?.id ?? null;
        selectedColorId.value = firstAvailable.color?.id ?? null;
        selectedVariantId.value = firstAvailable.id;
      }
    }

    // Fire view event
    void sendProductEvent({
      event_type: "view",
      product: data.id,
    });
  } catch (err) {
    error.value = toAppError(err).message;
  } finally {
    loading.value = false;
  }
}

async function handleAddToCart() {
  if (!currentStockStatus.value.available) {
    toast.show("Sản phẩm phiên bản này hiện đang hết hàng.", "error");
    return;
  }
  const variant = matchedVariant.value || product.value?.variants.find((v) => v.is_available);
  if (!variant) {
    toast.show("Vui lòng chọn size và phối màu hợp lệ.", "error");
    return;
  }
  await cartStore.addItem(variant.id, 1, getRecommendationAttribution(product.value?.id ?? 0));
}

async function handleWishlist(): Promise<void> {
  if (!product.value) return;
  if (!isAuthenticated.value) {
    toast.show("Vui lòng đăng nhập để lưu sản phẩm yêu thích.", "info");
    await router.push({ name: "login", query: { redirect: route.fullPath } });
    return;
  }
  try {
    const active = await wishlist.toggle(product.value.id);
    toast.show(active ? "Đã thêm vào yêu thích." : "Đã bỏ khỏi yêu thích.", "success");
  } catch {
    toast.show("Không thể cập nhật danh sách yêu thích.", "error");
  }
}

watch(
  () => route.params.slug,
  () => {
    void loadProduct();
  },
);

onMounted(() => {
  void loadProduct();
});
</script>

<template>
  <StorefrontLayout>
    <div class="min-h-screen pb-16 pt-6 sm:pt-10">
      <div class="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
        <!-- Breadcrumbs Navigation -->
        <nav class="mb-6 flex items-center gap-2 text-xs sm:text-sm font-semibold text-slate-400">
          <AppLink to="/" class="hover:text-emerald-400 no-underline text-slate-400">
            Trang chủ
          </AppLink>
          <span>/</span>
          <AppLink
            :to="{ name: 'products' }"
            class="hover:text-emerald-400 no-underline text-slate-400"
          >
            Sản phẩm
          </AppLink>
          <span>/</span>
          <AppLink
            v-if="product?.category"
            :to="{ name: 'products', query: { category: product.category.slug } }"
            class="hover:text-emerald-400 no-underline text-slate-400"
          >
            {{ product.category.name }}
          </AppLink>
          <span v-if="product?.category">/</span>
          <span class="text-white truncate max-w-[200px] sm:max-w-md">
            {{ product?.name || "Chi tiết sản phẩm" }}
          </span>
        </nav>

        <!-- Loading State -->
        <div v-if="loading" class="flex flex-col items-center justify-center p-20 text-slate-400">
          <svg class="h-10 w-10 animate-spin text-emerald-400 mb-4" viewBox="0 0 24 24" fill="none">
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
          <p class="text-base font-bold uppercase tracking-wider text-slate-300">
            Đang tải chi tiết sản phẩm…
          </p>
        </div>

        <!-- Error State -->
        <div
          v-else-if="error || !product"
          class="rounded-3xl border border-white/10 bg-[#12151e]/85 p-8 sm:p-12 text-center text-white backdrop-blur-xl"
        >
          <div
            class="mx-auto mb-4 flex h-16 w-16 items-center justify-center rounded-2xl bg-rose-500/10 text-rose-400 border border-rose-500/20"
          >
            <svg class="h-8 w-8" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path
                stroke-linecap="round"
                stroke-linejoin="round"
                stroke-width="2"
                d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z"
              />
            </svg>
          </div>
          <h2 class="text-2xl font-black uppercase tracking-tight">Không tìm thấy sản phẩm</h2>
          <p class="mt-2 text-sm text-slate-400 max-w-md mx-auto">
            {{ error || "Sản phẩm này hiện không khả dụng hoặc chưa được xuất bản." }}
          </p>
          <div class="mt-6">
            <AppLink
              to="/"
              class="inline-flex items-center gap-2 rounded-xl bg-emerald-500 px-6 py-3 text-sm font-black uppercase tracking-wider text-black no-underline hover:bg-emerald-400"
            >
              Quay lại cửa hàng
            </AppLink>
          </div>
        </div>

        <!-- Product Presentation Grid -->
        <div v-else class="grid gap-10 lg:grid-cols-12 lg:items-start">
          <!-- Gallery Section (7 Cols) -->
          <div class="lg:col-span-7 space-y-4">
            <!-- Main Hero Image Frame -->
            <div
              class="relative aspect-[4/3] w-full overflow-hidden rounded-3xl border border-white/10 bg-gradient-to-b from-[#161a26] to-[#0c0e15] shadow-[0_20px_50px_rgba(0,0,0,0.8)]"
            >
              <img
                :src="currentImage"
                :alt="product.name"
                class="h-full w-full object-cover object-center transition-transform duration-500 hover:scale-105"
              />

              <!-- Brand Floating Badge -->
              <div
                v-if="product.brand"
                class="absolute top-4 left-4 rounded-xl border border-white/20 bg-black/70 px-3.5 py-1.5 backdrop-blur-md"
              >
                <span class="text-xs font-black uppercase tracking-widest text-emerald-400">
                  {{ product.brand.name }}
                </span>
              </div>

              <!-- Availability Floating Tag -->
              <div
                class="absolute top-4 right-4 rounded-xl border px-3.5 py-1.5 backdrop-blur-md"
                :class="
                  currentStockStatus.available
                    ? 'border-emerald-500/30 bg-emerald-500/15 text-emerald-400'
                    : 'border-rose-500/30 bg-rose-500/15 text-rose-400'
                "
              >
                <span class="text-xs font-black uppercase tracking-wider">
                  {{ currentStockStatus.available ? "Còn hàng" : "Tạm hết" }}
                </span>
              </div>
            </div>

            <!-- Thumbnails Row -->
            <div
              v-if="product.images && product.images.length > 1"
              class="flex items-center gap-3 overflow-x-auto pb-2 scrollbar-none"
            >
              <button
                v-for="(img, idx) in product.images"
                :key="img.id"
                type="button"
                :class="[
                  'relative h-20 w-24 flex-shrink-0 overflow-hidden rounded-2xl border transition-all cursor-pointer',
                  activeImageIndex === idx
                    ? 'border-emerald-400 ring-2 ring-emerald-400/40'
                    : 'border-white/10 opacity-60 hover:opacity-100',
                ]"
                @click="activeImageIndex = idx"
              >
                <img
                  :src="img.image_url"
                  :alt="img.alt_text || product.name"
                  class="h-full w-full object-cover"
                />
              </button>
            </div>
          </div>

          <!-- Specifications & Actions Section (5 Cols) -->
          <div class="lg:col-span-5 space-y-6">
            <div
              class="rounded-3xl border border-white/10 bg-[#12151e]/85 backdrop-blur-xl p-6 sm:p-8 shadow-[0_25px_60px_-15px_rgba(0,0,0,0.9)] space-y-6"
            >
              <!-- Header Info -->
              <div class="space-y-2 border-b border-white/10 pb-6">
                <div class="flex items-center gap-2">
                  <span
                    v-if="product.category"
                    class="text-xs font-extrabold uppercase tracking-widest text-emerald-400"
                  >
                    {{ product.category.name }}
                  </span>
                  <span v-if="product.brand" class="text-xs text-slate-500 font-bold">•</span>
                  <span
                    v-if="product.brand"
                    class="text-xs font-bold uppercase tracking-wider text-slate-400"
                  >
                    {{ product.brand.name }}
                  </span>
                </div>

                <h1 class="text-2xl sm:text-3xl font-black uppercase tracking-tight text-white">
                  {{ product.name }}
                </h1>

                <!-- Price Display -->
                <div class="pt-2 flex items-baseline gap-3">
                  <span class="text-2xl sm:text-3xl font-black text-emerald-400">
                    {{ displayPrice }}
                  </span>
                </div>
              </div>

              <!-- Size Selection -->
              <div v-if="availableSizes.length > 0" class="space-y-3">
                <div class="flex items-center justify-between">
                  <label class="text-xs font-extrabold uppercase tracking-wider text-slate-200">
                    Chọn Size (Chuẩn Hãng)
                  </label>
                  <span
                    class="text-xs text-emerald-400 font-semibold cursor-pointer hover:underline"
                  >
                    Bảng size
                  </span>
                </div>
                <div class="grid grid-cols-4 gap-2">
                  <button
                    v-for="sz in availableSizes"
                    :key="sz.id"
                    type="button"
                    :disabled="!sz.available"
                    :class="[
                      'h-11 rounded-xl font-black text-sm uppercase transition-all cursor-pointer border',
                      selectedSizeId === sz.id
                        ? 'border-emerald-400 bg-emerald-500/20 text-emerald-400 shadow-[0_0_15px_rgba(16,185,129,0.3)]'
                        : sz.available
                          ? 'border-white/10 bg-white/5 text-slate-200 hover:border-white/30'
                          : 'border-white/5 bg-white/[0.02] text-slate-600 line-through cursor-not-allowed',
                    ]"
                    @click="selectedSizeId = sz.id"
                  >
                    {{ sz.label }}
                  </button>
                </div>
              </div>

              <!-- Color Selection -->
              <div v-if="availableColors.length > 0" class="space-y-3">
                <label class="text-xs font-extrabold uppercase tracking-wider text-slate-200 block">
                  Phối Màu
                </label>
                <div class="flex flex-wrap gap-3">
                  <button
                    v-for="c in availableColors"
                    :key="c.id"
                    type="button"
                    :class="[
                      'group flex items-center gap-2 rounded-xl border px-3 py-1.5 transition-all cursor-pointer',
                      selectedColorId === c.id
                        ? 'border-emerald-400 bg-emerald-500/15 text-white shadow-[0_0_15px_rgba(16,185,129,0.2)]'
                        : 'border-white/10 bg-white/5 text-slate-300 hover:border-white/25',
                    ]"
                    @click="selectedColorId = c.id"
                  >
                    <span
                      class="h-4 w-4 rounded-full border border-white/30"
                      :style="{ backgroundColor: c.hex }"
                    />
                    <span class="text-xs font-bold uppercase tracking-wider">{{ c.name }}</span>
                  </button>
                </div>
              </div>

              <div
                v-if="
                  availableSizes.length === 0 &&
                  availableColors.length === 0 &&
                  defaultVariant?.option_label
                "
                class="rounded-2xl border border-white/10 bg-white/5 p-4"
              >
                <p class="text-xs font-extrabold tracking-wider text-slate-400 uppercase">
                  Quy cách
                </p>
                <p class="mt-1 font-bold text-white">{{ defaultVariant.option_label }}</p>
              </div>

              <!-- Stock Balance / Availability Indicator -->
              <div
                class="flex items-center gap-2 rounded-2xl bg-white/5 border border-white/10 p-3.5"
              >
                <div
                  :class="[
                    'h-2.5 w-2.5 rounded-full',
                    currentStockStatus.available
                      ? 'bg-emerald-400 animate-pulse shadow-[0_0_8px_#10b981]'
                      : 'bg-rose-500',
                  ]"
                />
                <span class="text-xs font-bold text-slate-200">
                  <template v-if="currentStockStatus.available">
                    Sẵn sàng giao hàng ngay
                    <span v-if="currentStockStatus.quantity !== null" class="text-emerald-400">
                      ({{ currentStockStatus.quantity }} {{ unitLabel }} trong kho)
                    </span>
                  </template>
                  <template v-else> Sản phẩm hoặc phiên bản này tạm thời hết hàng </template>
                </span>
              </div>

              <!-- Add to Cart CTA -->
              <div class="grid gap-2 pt-2 sm:grid-cols-[1fr_auto]">
                <BaseButton
                  type="button"
                  block
                  :disabled="!currentStockStatus.available"
                  :class="[
                    'min-h-13 rounded-2xl text-sm font-black uppercase tracking-wider',
                    currentStockStatus.available
                      ? 'shadow-[0_15px_30px_rgba(16,185,129,0.35)]'
                      : 'opacity-50 cursor-not-allowed',
                  ]"
                  @click="handleAddToCart"
                >
                  {{ currentStockStatus.available ? "Thêm vào giỏ hàng" : "Hết hàng" }}
                </BaseButton>
                <BaseButton
                  type="button"
                  variant="secondary"
                  :aria-label="
                    wishlist.has(product.id) ? 'Bỏ khỏi yêu thích' : 'Thêm vào yêu thích'
                  "
                  @click="handleWishlist"
                >
                  {{ wishlist.has(product.id) ? "♥ Đã yêu thích" : "♡ Yêu thích" }}
                </BaseButton>
              </div>

              <!-- Product Description -->
              <div v-if="product.description" class="border-t border-white/10 pt-5">
                <h3 class="text-xs font-extrabold uppercase tracking-wider text-slate-400 mb-2">
                  Mô Tả Sản Phẩm
                </h3>
                <p class="text-sm leading-relaxed text-slate-300 whitespace-pre-line">
                  {{ product.description }}
                </p>
              </div>
            </div>
          </div>
        </div>
        <ReviewSection v-if="product" :product-id="product.id" :product-slug="product.slug" />
      </div>
    </div>
    <RecommendationRail
      v-if="product"
      mode="similar"
      :product-id="product.id"
      eyebrow="Phối trọn bộ"
      title="Sản phẩm tương tự & đi kèm"
      description="Khám phá lựa chọn cùng phong cách, tất thể thao và sản phẩm chăm sóc phù hợp."
      :limit="6"
    />
  </StorefrontLayout>
</template>
