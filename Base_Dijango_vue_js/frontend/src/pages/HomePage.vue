<script setup lang="ts">
import { computed, onMounted, ref } from "vue";
import { storeToRefs } from "pinia";

import SneakerHero3D from "@/components/home/SneakerHero3D.vue";
import AppLink from "@/components/navigation/AppLink.vue";
import StorefrontLayout from "@/layouts/StorefrontLayout.vue";
import { toAppError } from "@/lib/http/errors";
import { useAuthStore } from "@/modules/auth/stores/auth";
import { fetchProducts } from "@/modules/catalog/api";
import ProductCard from "@/modules/catalog/components/ProductCard.vue";
import RecommendationRail from "@/modules/catalog/components/RecommendationRail.vue";
import type { ProductListItem } from "@/modules/catalog/types";
import BannerSlot from "@/modules/engagement/components/BannerSlot.vue";

const { isAuthenticated } = storeToRefs(useAuthStore());
const apiProducts = ref<ProductListItem[]>([]);
const catalogLoading = ref(false);
const catalogError = ref("");
const featuredProducts = computed(() => apiProducts.value.slice(0, 6));

async function loadCatalog() {
  catalogLoading.value = true;
  catalogError.value = "";
  try {
    const prodRes = await fetchProducts({ ordering: "newest" });
    apiProducts.value = prodRes.results;
  } catch (err) {
    apiProducts.value = [];
    catalogError.value = toAppError(err).message;
  } finally {
    catalogLoading.value = false;
  }
}

onMounted(loadCatalog);
</script>

<template>
  <StorefrontLayout>
    <SneakerHero3D />

    <!-- 1. Clean, seamless marquee ticker -->
    <div
      class="relative flex overflow-hidden border-y border-white/10 bg-[#0d1017] py-2.5 text-xs font-semibold tracking-wider text-slate-300 select-none"
    >
      <div class="flex shrink-0 items-center gap-8 animate-marquee uppercase">
        <span class="flex items-center gap-4"
          >HẢI DUY SHOP <span class="text-emerald-400">•</span></span
        >
        <span class="flex items-center gap-4"
          >100% SẢN PHẨM CHÍNH HÃNG <span class="text-emerald-400">•</span></span
        >
        <span class="flex items-center gap-4"
          >GIAO HỎA TỐC NỘI THÀNH 2H <span class="text-emerald-400">•</span></span
        >
        <span class="flex items-center gap-4"
          >ĐỔI SIZE MIỄN PHÍ TRONG 30 NGÀY <span class="text-emerald-400">•</span></span
        >
        <span class="flex items-center gap-4"
          >BẢO HÀNH CHÍNH HÃNG TRỌN ĐỜI <span class="text-emerald-400">•</span></span
        >
        <span class="flex items-center gap-4"
          >HOT DROPS BỘ SƯU TẬP 2026 <span class="text-emerald-400">•</span></span
        >
        <span class="flex items-center gap-4"
          >HẢI DUY SHOP <span class="text-emerald-400">•</span></span
        >
        <span class="flex items-center gap-4"
          >100% SẢN PHẨM CHÍNH HÃNG <span class="text-emerald-400">•</span></span
        >
        <span class="flex items-center gap-4"
          >GIAO HỎA TỐC NỘI THÀNH 2H <span class="text-emerald-400">•</span></span
        >
        <span class="flex items-center gap-4"
          >ĐỔI SIZE MIỄN PHÍ TRONG 30 NGÀY <span class="text-emerald-400">•</span></span
        >
        <span class="flex items-center gap-4"
          >BẢO HÀNH CHÍNH HÃNG TRỌN ĐỜI <span class="text-emerald-400">•</span></span
        >
        <span class="flex items-center gap-4"
          >HOT DROPS BỘ SƯU TẬP 2026 <span class="text-emerald-400">•</span></span
        >
      </div>
      <div class="flex shrink-0 items-center gap-8 animate-marquee uppercase" aria-hidden="true">
        <span class="flex items-center gap-4"
          >HẢI DUY SHOP <span class="text-emerald-400">•</span></span
        >
        <span class="flex items-center gap-4"
          >100% SẢN PHẨM CHÍNH HÃNG <span class="text-emerald-400">•</span></span
        >
        <span class="flex items-center gap-4"
          >GIAO HỎA TỐC NỘI THÀNH 2H <span class="text-emerald-400">•</span></span
        >
        <span class="flex items-center gap-4"
          >ĐỔI SIZE MIỄN PHÍ TRONG 30 NGÀY <span class="text-emerald-400">•</span></span
        >
        <span class="flex items-center gap-4"
          >BẢO HÀNH CHÍNH HÃNG TRỌN ĐỜI <span class="text-emerald-400">•</span></span
        >
        <span class="flex items-center gap-4"
          >HOT DROPS BỘ SƯU TẬP 2026 <span class="text-emerald-400">•</span></span
        >
        <span class="flex items-center gap-4"
          >HẢI DUY SHOP <span class="text-emerald-400">•</span></span
        >
        <span class="flex items-center gap-4"
          >100% SẢN PHẨM CHÍNH HÃNG <span class="text-emerald-400">•</span></span
        >
        <span class="flex items-center gap-4"
          >GIAO HỎA TỐC NỘI THÀNH 2H <span class="text-emerald-400">•</span></span
        >
        <span class="flex items-center gap-4"
          >ĐỔI SIZE MIỄN PHÍ TRONG 30 NGÀY <span class="text-emerald-400">•</span></span
        >
        <span class="flex items-center gap-4"
          >BẢO HÀNH CHÍNH HÃNG TRỌN ĐỜI <span class="text-emerald-400">•</span></span
        >
        <span class="flex items-center gap-4"
          >HOT DROPS BỘ SƯU TẬP 2026 <span class="text-emerald-400">•</span></span
        >
      </div>
    </div>

    <BannerSlot position="home_strip" class="py-6" />

    <!-- 2. Featured products grid -->
    <section id="featured-collection" class="relative bg-[#090a0f] py-16 px-4 sm:px-6 lg:px-8">
      <div class="mx-auto max-w-7xl">
        <!-- Section Header & Filter Tabs -->
        <div class="flex flex-col justify-between gap-5 md:flex-row md:items-end">
          <div>
            <p class="text-xs font-bold tracking-widest text-emerald-400 uppercase">Bộ sưu tập</p>
            <h2 class="mt-1 text-2xl font-black uppercase text-white sm:text-4xl">
              SẢN PHẨM NỔI BẬT
            </h2>
          </div>

          <AppLink
            :to="{ name: 'products' }"
            class="inline-flex rounded-full border border-emerald-500/40 bg-emerald-500/10 px-5 py-2 text-xs font-black text-emerald-400 no-underline hover:bg-emerald-500 hover:text-black"
          >
            Xem tất cả sản phẩm
          </AppLink>
        </div>

        <div
          v-if="catalogLoading"
          class="mt-10 grid grid-cols-1 gap-6 sm:grid-cols-2 lg:grid-cols-3"
          aria-label="Đang tải sản phẩm"
        >
          <div
            v-for="index in 6"
            :key="index"
            class="aspect-[3/4] animate-pulse rounded-2xl border border-white/10 bg-white/5"
          />
        </div>
        <div
          v-else-if="catalogError"
          class="mt-10 rounded-2xl border border-rose-500/25 bg-rose-500/10 p-8 text-center"
        >
          <p class="font-bold text-rose-300">Không tải được sản phẩm từ hệ thống.</p>
          <p class="mt-2 text-sm text-slate-400">{{ catalogError }}</p>
        </div>
        <div
          v-else-if="featuredProducts.length"
          class="mt-10 grid grid-cols-1 gap-6 sm:grid-cols-2 lg:grid-cols-3"
        >
          <ProductCard v-for="product in featuredProducts" :key="product.id" :product="product" />
        </div>
        <div v-else class="py-16 text-center text-slate-400">
          <p class="text-sm">Catalog chưa có sản phẩm được xuất bản.</p>
          <AppLink
            :to="{ name: 'products' }"
            class="mt-3 inline-flex text-xs font-bold text-emerald-400"
          >
            Mở trang sản phẩm
          </AppLink>
        </div>
      </div>
    </section>

    <!-- 4. Category Showcase Section -->
    <section
      id="categories"
      class="border-t border-white/10 bg-[#07080c] py-16 px-4 sm:px-6 lg:px-8"
    >
      <div class="mx-auto max-w-7xl">
        <h2 class="text-center text-2xl font-black uppercase text-white sm:text-3xl">
          KHÁM PHÁ THEO DANH MỤC
        </h2>

        <div class="mt-10 grid grid-cols-1 gap-5 sm:grid-cols-2 lg:grid-cols-4">
          <!-- Running -->
          <AppLink
            :to="{ name: 'products', query: { category: 'running' } }"
            class="group relative aspect-[4/5] overflow-hidden rounded-2xl border border-white/10 no-underline"
          >
            <img
              src="https://images.unsplash.com/photo-1502680390469-be75c86b636f?auto=format&fit=crop&w=800&q=80"
              alt="Giày Chạy Bộ"
              class="h-full w-full object-cover transition-transform duration-500 group-hover:scale-105"
            />
            <div
              class="absolute inset-0 bg-gradient-to-t from-black/90 via-black/40 to-transparent"
            />
            <div class="absolute inset-x-4 bottom-4 always-white-text">
              <h3
                class="category-card-title text-lg font-black uppercase text-white drop-shadow-md"
              >
                Giày Chạy Bộ
              </h3>
              <p class="category-card-sub mt-0.5 text-xs text-slate-200 drop-shadow">
                Đệm êm phản hồi lực
              </p>
            </div>
          </AppLink>

          <!-- Basketball -->
          <AppLink
            :to="{ name: 'products', query: { category: 'basketball' } }"
            class="group relative aspect-[4/5] overflow-hidden rounded-2xl border border-white/10 no-underline"
          >
            <img
              src="https://images.unsplash.com/photo-1546519638-68e109498ffc?auto=format&fit=crop&w=800&q=80"
              alt="Giày Bóng Rổ"
              class="h-full w-full object-cover transition-transform duration-500 group-hover:scale-105"
            />
            <div
              class="absolute inset-0 bg-gradient-to-t from-black/90 via-black/40 to-transparent"
            />
            <div class="absolute inset-x-4 bottom-4 always-white-text">
              <h3
                class="category-card-title text-lg font-black uppercase text-white drop-shadow-md"
              >
                Giày Bóng Rổ
              </h3>
              <p class="category-card-sub mt-0.5 text-xs text-slate-200 drop-shadow">
                Khóa cổ chân & bám sàn
              </p>
            </div>
          </AppLink>

          <!-- Men Sneakers -->
          <AppLink
            :to="{ name: 'products', query: { category: 'men' } }"
            class="group relative aspect-[4/5] overflow-hidden rounded-2xl border border-white/10 no-underline"
          >
            <img
              src="https://images.unsplash.com/photo-1552346154-21d32810aba3?auto=format&fit=crop&w=800&q=80"
              alt="Sneakers Nam"
              class="h-full w-full object-cover transition-transform duration-500 group-hover:scale-105"
            />
            <div
              class="absolute inset-0 bg-gradient-to-t from-black/90 via-black/40 to-transparent"
            />
            <div class="absolute inset-x-4 bottom-4 always-white-text">
              <h3
                class="category-card-title text-lg font-black uppercase text-white drop-shadow-md"
              >
                Sneakers Nam
              </h3>
              <p class="category-card-sub mt-0.5 text-xs text-slate-200 drop-shadow">
                Phong cách streetwear
              </p>
            </div>
          </AppLink>

          <!-- Women Sneakers -->
          <AppLink
            :to="{ name: 'products', query: { category: 'women' } }"
            class="group relative aspect-[4/5] overflow-hidden rounded-2xl border border-white/10 no-underline"
          >
            <img
              src="https://images.unsplash.com/photo-1595950653106-6c9ebd614d3a?auto=format&fit=crop&w=800&q=80"
              alt="Sneakers Nữ"
              class="h-full w-full object-cover transition-transform duration-500 group-hover:scale-105"
            />
            <div
              class="absolute inset-0 bg-gradient-to-t from-black/90 via-black/40 to-transparent"
            />
            <div class="absolute inset-x-4 bottom-4 always-white-text">
              <h3
                class="category-card-title text-lg font-black uppercase text-white drop-shadow-md"
              >
                Sneakers Nữ
              </h3>
              <p class="category-card-sub mt-0.5 text-xs text-slate-200 drop-shadow">
                Thanh lịch và năng động
              </p>
            </div>
          </AppLink>
        </div>
      </div>
    </section>

    <!-- 5. Brand Commitments (Clean SVG Icons) -->
    <section class="border-t border-white/10 bg-[#090a0f] py-14 px-4 sm:px-6 lg:px-8">
      <div class="mx-auto max-w-7xl">
        <div class="grid grid-cols-1 gap-6 sm:grid-cols-2 lg:grid-cols-4">
          <!-- 1 -->
          <div class="rounded-xl border border-white/5 bg-white/[0.02] p-4">
            <div class="flex items-center gap-3">
              <div
                class="flex h-9 w-9 items-center justify-center rounded-lg bg-emerald-500/10 text-emerald-400"
              >
                <svg
                  class="h-5 w-5"
                  fill="none"
                  viewBox="0 0 24 24"
                  stroke="currentColor"
                  stroke-width="2"
                >
                  <path
                    stroke-linecap="round"
                    stroke-linejoin="round"
                    d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z"
                  />
                </svg>
              </div>
              <h4 class="text-sm font-bold text-white">100% Chính Hãng</h4>
            </div>
            <p class="mt-2 text-xs leading-relaxed text-slate-400">
              Cam kết hoàn tiền gấp đôi nếu phát hiện sản phẩm không chính hãng.
            </p>
          </div>

          <!-- 2 -->
          <div class="rounded-xl border border-white/5 bg-white/[0.02] p-4">
            <div class="flex items-center gap-3">
              <div
                class="flex h-9 w-9 items-center justify-center rounded-lg bg-emerald-500/10 text-emerald-400"
              >
                <svg
                  class="h-5 w-5"
                  fill="none"
                  viewBox="0 0 24 24"
                  stroke="currentColor"
                  stroke-width="2"
                >
                  <path
                    stroke-linecap="round"
                    stroke-linejoin="round"
                    d="M13 10V3L4 14h7v7l9-11h-7z"
                  />
                </svg>
              </div>
              <h4 class="text-sm font-bold text-white">Giao Hỏa Tốc 2H</h4>
            </div>
            <p class="mt-2 text-xs leading-relaxed text-slate-400">
              Giao hàng nhanh 2 giờ trong nội thành. Miễn phí vận chuyển đơn từ 1 triệu.
            </p>
          </div>

          <!-- 3 -->
          <div class="rounded-xl border border-white/5 bg-white/[0.02] p-4">
            <div class="flex items-center gap-3">
              <div
                class="flex h-9 w-9 items-center justify-center rounded-lg bg-emerald-500/10 text-emerald-400"
              >
                <svg
                  class="h-5 w-5"
                  fill="none"
                  viewBox="0 0 24 24"
                  stroke="currentColor"
                  stroke-width="2"
                >
                  <path
                    stroke-linecap="round"
                    stroke-linejoin="round"
                    d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15"
                  />
                </svg>
              </div>
              <h4 class="text-sm font-bold text-white">Đổi Size 30 Ngày</h4>
            </div>
            <p class="mt-2 text-xs leading-relaxed text-slate-400">
              Hỗ trợ đổi size tận nơi nhanh chóng, hoàn toàn an tâm khi mua hàng online.
            </p>
          </div>

          <!-- 4 -->
          <div class="rounded-xl border border-white/5 bg-white/[0.02] p-4">
            <div class="flex items-center gap-3">
              <div
                class="flex h-9 w-9 items-center justify-center rounded-lg bg-emerald-500/10 text-emerald-400"
              >
                <svg
                  class="h-5 w-5"
                  fill="none"
                  viewBox="0 0 24 24"
                  stroke="currentColor"
                  stroke-width="2"
                >
                  <path
                    stroke-linecap="round"
                    stroke-linejoin="round"
                    d="M11 4a2 2 0 114 0v1a1 1 0 001 1h3a1 1 0 011 1v3a1 1 0 01-1 1h-1a2 2 0 100 4h1a1 1 0 011 1v3a1 1 0 01-1 1h-3a1 1 0 01-1-1v-1a2 2 0 10-4 0v1a1 1 0 01-1 1H7a1 1 0 01-1-1v-3a1 1 0 00-1-1H4a2 2 0 110-4h1a1 1 0 001-1V7a1 1 0 011-1h3a1 1 0 001-1V4z"
                  />
                </svg>
              </div>
              <h4 class="text-sm font-bold text-white">Bảo Hành Trọn Đời</h4>
            </div>
            <p class="mt-2 text-xs leading-relaxed text-slate-400">
              Bảo hành keo dán và đường may trọn đời sản phẩm tại showroom Hải Duy.
            </p>
          </div>
        </div>
      </div>
    </section>

    <RecommendationRail
      mode="popular"
      eyebrow="Xu hướng cộng đồng"
      title="Được quan tâm nhiều nhất"
      description="Tổng hợp từ lượt xem, yêu thích, thêm giỏ và đơn hàng đã hoàn tất gần đây."
      :limit="6"
    />

    <RecommendationRail
      v-if="isAuthenticated"
      mode="personalized"
      eyebrow="Riêng cho tài khoản của bạn"
      title="Có thể bạn sẽ thích"
      description="Gợi ý từ những sản phẩm bạn đã xem, yêu thích và mua trước đây."
      :limit="6"
    />

    <!-- 6. Account Management / Membership Section -->
    <section class="border-t border-white/10 bg-[#07080c] py-14 px-4 sm:px-6 lg:px-8 text-center">
      <div class="mx-auto max-w-2xl space-y-4">
        <h3 class="text-xl font-black uppercase text-white sm:text-2xl">THÀNH VIÊN HẢI DUY SHOP</h3>
        <p class="text-xs text-slate-400">
          Tạo tài khoản để quản lý đơn hàng, lưu danh sách yêu thích và nhận thông tin các đợt phát
          hành giày mới.
        </p>
        <div class="flex justify-center gap-3 pt-2">
          <AppLink
            v-if="!isAuthenticated"
            to="/register"
            class="rounded-full bg-emerald-500 px-6 py-2.5 text-xs font-bold text-black uppercase no-underline transition hover:bg-emerald-400"
          >
            Đăng ký tài khoản
          </AppLink>
          <AppLink
            v-if="!isAuthenticated"
            to="/login"
            class="rounded-full border border-white/20 bg-white/5 px-6 py-2.5 text-xs font-semibold text-white uppercase no-underline transition hover:bg-white/10"
          >
            Đăng nhập
          </AppLink>
          <AppLink
            v-else
            to="/profile"
            class="rounded-full bg-emerald-500 px-6 py-2.5 text-xs font-bold text-black uppercase no-underline transition hover:bg-emerald-400"
          >
            Quản lý tài khoản của bạn
          </AppLink>
        </div>
      </div>
    </section>
  </StorefrontLayout>
</template>

<style scoped>
@keyframes marquee {
  0% {
    transform: translateX(0%);
  }
  100% {
    transform: translateX(-100%);
  }
}

.animate-marquee {
  display: flex;
  min-width: 100%;
  animation: marquee 26s linear infinite;
}

@media (prefers-reduced-motion: reduce) {
  .animate-marquee {
    animation: none;
  }
}
</style>
