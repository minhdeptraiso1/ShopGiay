<script setup lang="ts">
import { computed, onMounted, ref } from "vue";

import BaseButton from "@/components/base/BaseButton.vue";
import AppAlert from "@/components/feedback/AppAlert.vue";
import AppLink from "@/components/navigation/AppLink.vue";
import AdminLayout from "@/layouts/AdminLayout.vue";
import { toAppError } from "@/lib/http/errors";
import {
  fetchAdminBrands,
  fetchAdminCategories,
  fetchAdminColors,
  fetchAdminSizes,
  type AdminBrand,
  type AdminCategory,
  type AdminColor,
  type AdminSize,
} from "../api";

const brands = ref<AdminBrand[]>([]);
const categories = ref<AdminCategory[]>([]);
const colors = ref<AdminColor[]>([]);
const sizes = ref<AdminSize[]>([]);
const loading = ref(true);
const error = ref("");

const activeBrands = computed(() => brands.value.filter((item) => item.is_active));
const activeCategories = computed(() => categories.value.filter((item) => item.is_active));
const activeColors = computed(() => colors.value.filter((item) => item.is_active));
const activeSizes = computed(() => sizes.value.filter((item) => item.is_active));

const brandSizeGroups = computed(() =>
  activeBrands.value.map((brand) => ({
    ...brand,
    sizes: activeSizes.value
      .filter((size) => size.brand === brand.id)
      .sort((a, b) => a.sort_order - b.sort_order),
  })),
);

async function loadSettings() {
  loading.value = true;
  error.value = "";
  try {
    const [brandData, categoryData, colorData, sizeData] = await Promise.all([
      fetchAdminBrands(),
      fetchAdminCategories(),
      fetchAdminColors(),
      fetchAdminSizes(),
    ]);
    brands.value = brandData;
    categories.value = categoryData;
    colors.value = colorData;
    sizes.value = sizeData;
  } catch (requestError) {
    error.value = toAppError(requestError).message;
  } finally {
    loading.value = false;
  }
}

onMounted(loadSettings);
</script>

<template>
  <AdminLayout>
    <div class="space-y-7">
      <header
        class="flex flex-col gap-4 border-b border-white/10 pb-6 sm:flex-row sm:items-end sm:justify-between"
      >
        <div>
          <p class="text-xs font-black tracking-[0.18em] text-emerald-400 uppercase">
            Nền tảng catalog
          </p>
          <h1 class="mt-2 text-2xl font-black tracking-tight text-white sm:text-3xl">
            Thiết lập một lần, dùng cho mọi sản phẩm
          </h1>
          <p class="mt-2 max-w-3xl text-sm leading-6 text-slate-400">
            Tạo danh mục và thương hiệu trước, sau đó khai báo bảng size theo từng hãng và bảng màu
            dùng chung. Khi tạo sản phẩm hoặc SKU, chỉ cần chọn lại dữ liệu đã chuẩn hóa ở đây.
          </p>
        </div>
        <BaseButton
          type="button"
          variant="secondary"
          size="sm"
          :loading="loading"
          @click="loadSettings"
          >Làm mới dữ liệu</BaseButton
        >
      </header>

      <AppAlert v-if="error" variant="error" title="Không tải được thiết lập catalog">{{
        error
      }}</AppAlert>

      <section
        class="rounded-2xl border border-emerald-500/20 bg-emerald-500/[0.06] p-5 sm:p-6"
        aria-labelledby="catalog-flow-title"
      >
        <p class="text-xs font-black tracking-wider text-emerald-400 uppercase">Luồng đề xuất</p>
        <h2 id="catalog-flow-title" class="mt-1 text-lg font-black text-white">
          Tạo catalog theo đúng thứ tự
        </h2>
        <ol class="mt-5 grid gap-3 md:grid-cols-4">
          <li
            v-for="step in [
              { number: '01', title: 'Danh mục', text: 'Phân loại mục đích sử dụng' },
              { number: '02', title: 'Thương hiệu', text: 'Chủ sở hữu bảng size' },
              { number: '03', title: 'Size & màu', text: 'Thuộc tính dùng cho SKU' },
              { number: '04', title: 'Sản phẩm', text: 'Tạo nội dung rồi sinh biến thể' },
            ]"
            :key="step.number"
            class="rounded-xl border border-white/10 bg-[#0c0e17]/70 p-4"
          >
            <span class="text-xs font-black text-emerald-400">{{ step.number }}</span>
            <strong class="mt-2 block text-sm text-white">{{ step.title }}</strong>
            <span class="mt-1 block text-xs leading-5 text-slate-400">{{ step.text }}</span>
          </li>
        </ol>
      </section>

      <div v-if="loading" class="grid gap-4 md:grid-cols-2" aria-label="Đang tải thiết lập catalog">
        <div
          v-for="index in 4"
          :key="index"
          class="h-48 animate-pulse rounded-2xl border border-white/10 bg-white/5"
        />
      </div>

      <section v-else class="grid gap-4 md:grid-cols-2">
        <article class="rounded-2xl border border-white/10 bg-[#12151e] p-5 sm:p-6">
          <div class="flex items-start justify-between gap-4">
            <div>
              <p class="text-xs font-black tracking-wider text-teal-400 uppercase">Phân loại</p>
              <h2 class="mt-1 text-xl font-black text-white">Danh mục</h2>
            </div>
            <span class="rounded-xl bg-teal-400/10 px-3 py-2 text-lg font-black text-teal-300">{{
              activeCategories.length
            }}</span>
          </div>
          <div class="mt-5 flex flex-wrap gap-2">
            <span
              v-for="category in activeCategories.slice(0, 8)"
              :key="category.id"
              class="rounded-full border border-white/10 bg-white/5 px-3 py-1.5 text-xs font-semibold text-slate-300"
              >{{ category.name }}</span
            >
            <span v-if="activeCategories.length === 0" class="text-sm text-slate-500"
              >Chưa có danh mục hoạt động.</span
            >
          </div>
          <AppLink
            to="/admin/categories"
            class="mt-6 inline-flex rounded-xl border border-white/10 bg-white/5 px-4 py-2 text-xs text-white no-underline hover:border-teal-400/30 hover:bg-teal-400/10"
            >Quản lý danh mục →</AppLink
          >
        </article>

        <article class="rounded-2xl border border-white/10 bg-[#12151e] p-5 sm:p-6">
          <div class="flex items-start justify-between gap-4">
            <div>
              <p class="text-xs font-black tracking-wider text-amber-300 uppercase">Nhà sản xuất</p>
              <h2 class="mt-1 text-xl font-black text-white">Thương hiệu</h2>
            </div>
            <span class="rounded-xl bg-amber-400/10 px-3 py-2 text-lg font-black text-amber-300">{{
              activeBrands.length
            }}</span>
          </div>
          <div class="mt-5 grid grid-cols-2 gap-2 sm:grid-cols-3">
            <div
              v-for="brand in activeBrands.slice(0, 6)"
              :key="brand.id"
              class="rounded-xl border border-white/8 bg-white/[0.025] p-3"
            >
              <strong class="block text-sm text-white">{{ brand.name }}</strong
              ><span class="mt-1 block text-[11px] text-slate-500"
                >{{
                  brandSizeGroups.find((item) => item.id === brand.id)?.sizes.length || 0
                }}
                size</span
              >
            </div>
            <span v-if="activeBrands.length === 0" class="text-sm text-slate-500"
              >Chưa có thương hiệu hoạt động.</span
            >
          </div>
          <AppLink
            to="/admin/brands"
            class="mt-6 inline-flex rounded-xl border border-white/10 bg-white/5 px-4 py-2 text-xs text-white no-underline hover:border-amber-400/30 hover:bg-amber-400/10"
            >Quản lý thương hiệu →</AppLink
          >
        </article>

        <article class="rounded-2xl border border-white/10 bg-[#12151e] p-5 sm:p-6">
          <div class="flex items-start justify-between gap-4">
            <div>
              <p class="text-xs font-black tracking-wider text-sky-300 uppercase">Theo từng hãng</p>
              <h2 class="mt-1 text-xl font-black text-white">Hệ thống kích cỡ</h2>
            </div>
            <span class="rounded-xl bg-sky-400/10 px-3 py-2 text-lg font-black text-sky-300">{{
              activeSizes.length
            }}</span>
          </div>
          <div class="mt-5 space-y-3">
            <div
              v-for="group in brandSizeGroups.slice(0, 4)"
              :key="group.id"
              class="grid grid-cols-[6rem_1fr] items-start gap-3"
            >
              <span class="truncate text-xs font-bold text-slate-300">{{ group.name }}</span>
              <div class="flex flex-wrap gap-1.5">
                <span
                  v-for="size in group.sizes.slice(0, 7)"
                  :key="size.id"
                  class="grid h-7 min-w-7 place-items-center rounded-lg bg-white/5 px-2 text-[11px] font-bold text-slate-300"
                  >{{ size.label }}</span
                ><span v-if="group.sizes.length === 0" class="text-xs text-amber-300"
                  >Chưa có size</span
                >
              </div>
            </div>
          </div>
          <AppLink
            to="/admin/sizes"
            class="mt-6 inline-flex rounded-xl border border-white/10 bg-white/5 px-4 py-2 text-xs text-white no-underline hover:border-sky-400/30 hover:bg-sky-400/10"
            >Quản lý bảng size →</AppLink
          >
        </article>

        <article class="rounded-2xl border border-white/10 bg-[#12151e] p-5 sm:p-6">
          <div class="flex items-start justify-between gap-4">
            <div>
              <p class="text-xs font-black tracking-wider text-rose-300 uppercase">Dùng chung</p>
              <h2 class="mt-1 text-xl font-black text-white">Bảng màu</h2>
            </div>
            <span class="rounded-xl bg-rose-400/10 px-3 py-2 text-lg font-black text-rose-300">{{
              activeColors.length
            }}</span>
          </div>
          <div class="mt-5 grid grid-cols-2 gap-2 sm:grid-cols-3">
            <div
              v-for="color in activeColors.slice(0, 9)"
              :key="color.id"
              class="flex items-center gap-2 rounded-xl border border-white/8 bg-white/[0.025] p-2.5"
            >
              <span
                class="h-5 w-5 rounded-full border border-white/20"
                :style="{ backgroundColor: color.hex_code || '#64748b' }"
              /><span class="truncate text-xs font-semibold text-slate-300">{{ color.name }}</span>
            </div>
            <span v-if="activeColors.length === 0" class="text-sm text-slate-500"
              >Chưa có màu hoạt động.</span
            >
          </div>
          <AppLink
            to="/admin/colors"
            class="mt-6 inline-flex rounded-xl border border-white/10 bg-white/5 px-4 py-2 text-xs text-white no-underline hover:border-rose-400/30 hover:bg-rose-400/10"
            >Quản lý bảng màu →</AppLink
          >
        </article>
      </section>

      <section
        class="flex flex-col gap-4 rounded-2xl border border-white/10 bg-[#12151e] p-5 sm:flex-row sm:items-center sm:justify-between sm:p-6"
      >
        <div>
          <p class="text-xs font-black tracking-wider text-emerald-400 uppercase">
            Đã thiết lập xong?
          </p>
          <h2 class="mt-1 text-lg font-black text-white">
            Tiếp tục tạo sản phẩm và các SKU bán hàng
          </h2>
          <p class="mt-1 text-sm text-slate-400">
            Sản phẩm giữ nội dung chung; biến thể giữ size, màu, giá và tồn kho.
          </p>
        </div>
        <div class="flex gap-3">
          <AppLink
            to="/admin/products"
            class="rounded-xl bg-emerald-500 px-4 py-2.5 text-xs font-black text-black no-underline hover:bg-emerald-400"
            >Tạo sản phẩm</AppLink
          ><AppLink
            to="/admin/variants"
            class="rounded-xl border border-white/10 bg-white/5 px-4 py-2.5 text-xs font-bold text-white no-underline hover:bg-white/10"
            >Quản lý SKU</AppLink
          >
        </div>
      </section>
    </div>
  </AdminLayout>
</template>
