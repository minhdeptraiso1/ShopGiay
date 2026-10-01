<script setup lang="ts">
import { computed, onMounted, ref, watch } from "vue";
import { useRoute, useRouter } from "vue-router";

import BaseButton from "@/components/base/BaseButton.vue";
import BaseInput from "@/components/base/BaseInput.vue";
import AppLink from "@/components/navigation/AppLink.vue";
import StorefrontLayout from "@/layouts/StorefrontLayout.vue";
import { toAppError } from "@/lib/http/errors";
import BannerSlot from "@/modules/engagement/components/BannerSlot.vue";
import { fetchBrands, fetchCategories, fetchProducts } from "../api";
import ProductCard from "../components/ProductCard.vue";
import type { Brand, Category, ProductListItem, ProductQueryParams } from "../types";

const route = useRoute();
const router = useRouter();

const products = ref<ProductListItem[]>([]);
const categories = ref<Category[]>([]);
const brands = ref<Brand[]>([]);
const count = ref(0);
const loading = ref(true);
const error = ref("");
const searchInput = ref("");

const queryValue = (value: unknown) => (typeof value === "string" ? value : "");
const currentPage = computed(() => Math.max(1, Number(queryValue(route.query.page)) || 1));
const selectedCategory = computed(() => queryValue(route.query.category));
const selectedBrand = computed(() => queryValue(route.query.brand));
const inStockOnly = computed(() => queryValue(route.query.in_stock) === "true");
const selectedOrdering = computed<ProductQueryParams["ordering"]>(() => {
  const value = queryValue(route.query.ordering);
  return ["newest", "name", "-name", "price", "-price"].includes(value)
    ? (value as ProductQueryParams["ordering"])
    : "newest";
});
const firstVisible = computed(() => (count.value === 0 ? 0 : (currentPage.value - 1) * 20 + 1));
const lastVisible = computed(() => Math.min(currentPage.value * 20, count.value));

function routeQuery(overrides: Record<string, string | undefined>) {
  const next = { ...route.query, ...overrides };
  return Object.fromEntries(
    Object.entries(next).filter(([, value]) => value !== undefined && value !== ""),
  );
}

async function loadFacets() {
  const [categoryData, brandData] = await Promise.all([fetchCategories(), fetchBrands()]);
  categories.value = categoryData;
  brands.value = brandData;
}

async function loadProducts() {
  loading.value = true;
  error.value = "";
  searchInput.value = queryValue(route.query.q);
  try {
    const response = await fetchProducts({
      search: searchInput.value || undefined,
      category: selectedCategory.value || undefined,
      brand: selectedBrand.value || undefined,
      in_stock: inStockOnly.value || undefined,
      ordering: selectedOrdering.value,
      page: currentPage.value,
    });
    products.value = response.results;
    count.value = response.count;
  } catch (err) {
    products.value = [];
    count.value = 0;
    error.value = toAppError(err).message;
  } finally {
    loading.value = false;
  }
}

function submitSearch() {
  void router.push({
    name: "products",
    query: routeQuery({ q: searchInput.value.trim(), page: undefined }),
  });
}

function clearFilters() {
  searchInput.value = "";
  void router.push({ name: "products" });
}

function changePage(page: number) {
  void router.push({
    name: "products",
    query: routeQuery({ page: page > 1 ? String(page) : undefined }),
  });
}

watch(() => route.fullPath, loadProducts);

onMounted(async () => {
  try {
    await Promise.all([loadFacets(), loadProducts()]);
  } catch (err) {
    error.value = toAppError(err).message;
    loading.value = false;
  }
});
</script>

<template>
  <StorefrontLayout>
    <section class="border-b border-white/10 bg-[#0d1017] px-4 py-12 sm:px-6 lg:px-8">
      <div class="mx-auto max-w-7xl">
        <nav class="text-xs font-semibold text-slate-400" aria-label="Đường dẫn">
          <AppLink to="/" class="text-slate-400 no-underline hover:text-emerald-400">
            Trang chủ
          </AppLink>
          <span class="mx-2">/</span><span class="text-white">Sản phẩm</span>
        </nav>
        <div class="mt-5 max-w-2xl">
          <p class="text-xs font-black tracking-[0.2em] text-emerald-400 uppercase">
            Catalog chính hãng
          </p>
          <h1 class="mt-2 text-3xl font-black tracking-tight text-white uppercase sm:text-5xl">
            Tất cả sản phẩm
          </h1>
          <p class="mt-3 text-sm leading-6 text-slate-400 sm:text-base">
            Tìm đôi giày phù hợp theo danh mục, thương hiệu và tình trạng tồn kho thực tế.
          </p>
        </div>
      </div>
    </section>

    <BannerSlot position="products_top" class="pt-8" />

    <section class="bg-[#090a0f] px-4 py-10 sm:px-6 lg:px-8">
      <div class="mx-auto max-w-7xl">
        <form class="flex flex-col gap-3 sm:flex-row" role="search" @submit.prevent="submitSearch">
          <BaseInput
            id="catalog-search"
            v-model="searchInput"
            name="catalog_search"
            placeholder="Tìm theo tên, SKU, thương hiệu..."
            aria-label="Tìm sản phẩm"
          />
          <BaseButton type="submit" class="sm:w-auto">Tìm kiếm</BaseButton>
        </form>

        <div class="mt-6 grid gap-5 lg:grid-cols-[240px_minmax(0,1fr)]">
          <aside
            class="space-y-6 rounded-2xl border border-white/10 bg-white/[0.02] p-5"
            aria-label="Bộ lọc sản phẩm"
          >
            <div>
              <h2 class="text-xs font-black tracking-wider text-white uppercase">Danh mục</h2>
              <div class="mt-3 flex flex-wrap gap-2 lg:flex-col lg:items-start">
                <AppLink
                  :to="{
                    name: 'products',
                    query: routeQuery({ category: undefined, page: undefined }),
                  }"
                  :class="selectedCategory ? 'text-slate-400' : 'text-emerald-400'"
                  class="no-underline"
                >
                  Tất cả danh mục
                </AppLink>
                <AppLink
                  v-for="category in categories"
                  :key="category.id"
                  :to="{
                    name: 'products',
                    query: routeQuery({ category: category.slug, page: undefined }),
                  }"
                  :class="
                    selectedCategory === category.slug ? 'text-emerald-400' : 'text-slate-400'
                  "
                  class="no-underline"
                >
                  {{ category.name }}
                </AppLink>
              </div>
            </div>

            <div class="border-t border-white/10 pt-5">
              <h2 class="text-xs font-black tracking-wider text-white uppercase">Thương hiệu</h2>
              <div class="mt-3 flex flex-wrap gap-2 lg:flex-col lg:items-start">
                <AppLink
                  :to="{
                    name: 'products',
                    query: routeQuery({ brand: undefined, page: undefined }),
                  }"
                  :class="selectedBrand ? 'text-slate-400' : 'text-emerald-400'"
                  class="no-underline"
                >
                  Tất cả thương hiệu
                </AppLink>
                <AppLink
                  v-for="brand in brands"
                  :key="brand.id"
                  :to="{
                    name: 'products',
                    query: routeQuery({ brand: brand.slug, page: undefined }),
                  }"
                  :class="selectedBrand === brand.slug ? 'text-emerald-400' : 'text-slate-400'"
                  class="no-underline"
                >
                  {{ brand.name }}
                </AppLink>
              </div>
            </div>

            <div class="border-t border-white/10 pt-5">
              <AppLink
                :to="{
                  name: 'products',
                  query: routeQuery({
                    in_stock: inStockOnly ? undefined : 'true',
                    page: undefined,
                  }),
                }"
                :class="
                  inStockOnly
                    ? 'border-emerald-500/40 bg-emerald-500/15 text-emerald-400'
                    : 'border-white/10 bg-white/5 text-slate-300'
                "
                class="inline-flex rounded-full border px-3 py-2 text-xs no-underline"
              >
                Chỉ xem sản phẩm còn hàng
              </AppLink>
            </div>

            <BaseButton type="button" variant="ghost" size="sm" block @click="clearFilters">
              Xóa bộ lọc
            </BaseButton>
          </aside>

          <div>
            <div
              class="flex flex-col gap-4 border-b border-white/10 pb-5 sm:flex-row sm:items-center sm:justify-between"
            >
              <p class="text-sm font-semibold text-slate-400">
                <template v-if="!loading">
                  Hiển thị {{ firstVisible }}–{{ lastVisible }} trong {{ count }} sản phẩm
                </template>
                <template v-else>Đang tải sản phẩm...</template>
              </p>
              <div class="flex flex-wrap gap-2 text-xs">
                <AppLink
                  v-for="option in [
                    { value: 'newest', label: 'Mới nhất' },
                    { value: 'price', label: 'Giá thấp' },
                    { value: '-price', label: 'Giá cao' },
                  ]"
                  :key="option.value"
                  :to="{
                    name: 'products',
                    query: routeQuery({
                      ordering: option.value === 'newest' ? undefined : option.value,
                      page: undefined,
                    }),
                  }"
                  :class="
                    selectedOrdering === option.value
                      ? 'bg-emerald-500 text-black'
                      : 'bg-white/5 text-slate-300'
                  "
                  class="rounded-full px-3 py-2 no-underline"
                >
                  {{ option.label }}
                </AppLink>
              </div>
            </div>

            <div
              v-if="loading"
              class="mt-6 grid grid-cols-1 gap-6 sm:grid-cols-2 xl:grid-cols-3"
              aria-label="Đang tải sản phẩm"
            >
              <div
                v-for="index in 6"
                :key="index"
                class="aspect-[3/4] animate-pulse rounded-2xl border border-white/10 bg-white/5"
              />
            </div>

            <div
              v-else-if="error"
              class="mt-6 rounded-2xl border border-rose-500/25 bg-rose-500/10 p-8 text-center"
            >
              <h2 class="font-black text-rose-300">Không tải được sản phẩm</h2>
              <p class="mt-2 text-sm text-slate-300">{{ error }}</p>
              <BaseButton type="button" size="sm" class="mt-5" @click="loadProducts">
                Thử lại
              </BaseButton>
            </div>

            <div
              v-else-if="products.length === 0"
              class="mt-6 rounded-2xl border border-white/10 bg-white/[0.02] p-10 text-center"
            >
              <h2 class="text-xl font-black text-white">Không tìm thấy sản phẩm phù hợp</h2>
              <p class="mt-2 text-sm text-slate-400">Hãy thử từ khóa hoặc bộ lọc khác.</p>
              <BaseButton type="button" size="sm" class="mt-5" @click="clearFilters">
                Xem tất cả
              </BaseButton>
            </div>

            <div v-else class="mt-6 grid grid-cols-1 gap-6 sm:grid-cols-2 xl:grid-cols-3">
              <ProductCard v-for="product in products" :key="product.id" :product="product" />
            </div>

            <div
              v-if="!loading && !error && count > 20"
              class="mt-8 flex items-center justify-center gap-3"
            >
              <BaseButton
                type="button"
                variant="secondary"
                size="sm"
                :disabled="currentPage <= 1"
                @click="changePage(currentPage - 1)"
              >
                Trang trước
              </BaseButton>
              <span class="text-sm font-bold text-slate-300">Trang {{ currentPage }}</span>
              <BaseButton
                type="button"
                variant="secondary"
                size="sm"
                :disabled="lastVisible >= count"
                @click="changePage(currentPage + 1)"
              >
                Trang sau
              </BaseButton>
            </div>
          </div>
        </div>
      </div>
    </section>
  </StorefrontLayout>
</template>
