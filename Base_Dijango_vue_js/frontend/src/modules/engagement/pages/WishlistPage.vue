<script setup lang="ts">
import { onMounted } from "vue";

import AppAlert from "@/components/feedback/AppAlert.vue";
import AppLink from "@/components/navigation/AppLink.vue";
import StorefrontLayout from "@/layouts/StorefrontLayout.vue";
import ProductCard from "@/modules/catalog/components/ProductCard.vue";
import { useWishlistStore } from "../stores/wishlist";

const wishlist = useWishlistStore();
onMounted(() => void wishlist.load());
</script>

<template>
  <StorefrontLayout>
    <main class="mx-auto min-h-[70vh] max-w-7xl px-4 py-10 sm:px-6 lg:px-8">
      <p class="text-xs font-black tracking-widest text-emerald-400 uppercase">
        Bộ sưu tập cá nhân
      </p>
      <h1 class="mt-2 text-3xl font-black text-white sm:text-4xl">Sản phẩm yêu thích</h1>
      <p class="mt-2 text-sm text-slate-400">Lưu những đôi giày bạn muốn quay lại xem sau.</p>
      <p v-if="wishlist.loading" class="py-16 text-center text-slate-400">Đang tải danh sách…</p>
      <AppAlert
        v-else-if="wishlist.error"
        class="mt-8"
        variant="error"
        title="Không tải được wishlist"
        >{{ wishlist.error }}</AppAlert
      >
      <div
        v-else-if="wishlist.items.length"
        class="mt-8 grid gap-5 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4"
      >
        <ProductCard v-for="item in wishlist.items" :key="item.id" :product="item.product" />
      </div>
      <div
        v-else
        class="mt-8 rounded-3xl border border-dashed border-white/15 bg-white/5 p-12 text-center"
      >
        <h2 class="text-lg font-black text-white">Danh sách đang trống</h2>
        <p class="mt-2 text-sm text-slate-400">
          Nhấn biểu tượng trái tim trên sản phẩm để lưu lại.
        </p>
        <AppLink
          to="/products"
          class="mt-5 inline-flex min-h-12 items-center rounded-xl bg-emerald-500 px-5 text-sm font-black tracking-wider text-black uppercase no-underline"
          >Khám phá sản phẩm</AppLink
        >
      </div>
    </main>
  </StorefrontLayout>
</template>
