<script setup lang="ts">
import { computed } from "vue";
import { useRouter } from "vue-router";

import { useToastStore } from "@/app/stores/toast";
import BaseButton from "@/components/base/BaseButton.vue";
import AppLink from "@/components/navigation/AppLink.vue";
import { useAuth } from "@/modules/auth/composables/useAuth";
import { useWishlistStore } from "@/modules/engagement/stores/wishlist";
import type { ProductListItem } from "../types";

const props = defineProps<{ product: ProductListItem }>();
const emit = defineEmits<{ select: [productId: number] }>();
const router = useRouter();
const toast = useToastStore();
const { isAuthenticated } = useAuth();
const wishlist = useWishlistStore();

async function handleWishlist(): Promise<void> {
  if (!isAuthenticated.value) {
    toast.show("Vui lòng đăng nhập để lưu sản phẩm yêu thích.", "info");
    await router.push({ name: "login", query: { redirect: router.currentRoute.value.fullPath } });
    return;
  }

  try {
    const active = await wishlist.toggle(props.product.id);
    toast.show(
      active ? "Đã thêm vào danh sách yêu thích." : "Đã bỏ khỏi danh sách yêu thích.",
      "success",
    );
  } catch {
    toast.show("Không thể cập nhật danh sách yêu thích.", "error");
  }
}

const priceLabel = computed(() => {
  if (!props.product.min_price) return "Liên hệ";
  const formatter = new Intl.NumberFormat("vi-VN", { style: "currency", currency: "VND" });
  const minPrice = formatter.format(Number(props.product.min_price));
  if (props.product.max_price && props.product.max_price !== props.product.min_price) {
    return `${minPrice} – ${formatter.format(Number(props.product.max_price))}`;
  }
  return minPrice;
});
</script>

<template>
  <article
    class="group flex h-full flex-col overflow-hidden rounded-2xl border border-white/10 bg-white/[0.02] p-3.5 transition-all duration-200 hover:-translate-y-1 hover:border-emerald-500/35 hover:bg-white/[0.04]"
  >
    <div class="relative">
      <AppLink
        :to="{ name: 'product-detail', params: { slug: product.slug } }"
        class="relative block aspect-square w-full overflow-hidden rounded-xl bg-[#11141d] no-underline"
        @click="emit('select', product.id)"
      >
        <img
          v-if="product.primary_image?.image_url"
          :src="product.primary_image.image_url"
          :alt="product.primary_image.alt_text || product.name"
          loading="lazy"
          class="h-full w-full object-cover object-center transition-transform duration-300 group-hover:scale-105"
        />
        <div
          v-else
          class="grid h-full place-items-center text-center text-slate-500"
          role="img"
          :aria-label="`Chưa có ảnh cho ${product.name}`"
        >
          <div>
            <svg
              class="mx-auto h-10 w-10"
              fill="none"
              viewBox="0 0 24 24"
              stroke="currentColor"
              stroke-width="1.5"
              aria-hidden="true"
            >
              <path
                stroke-linecap="round"
                stroke-linejoin="round"
                d="m2.25 15.75 5.159-5.159a2.25 2.25 0 0 1 3.182 0l5.159 5.159m-1.5-1.5 1.409-1.409a2.25 2.25 0 0 1 3.182 0l2.909 2.909m-18 3.75h16.5a1.5 1.5 0 0 0 1.5-1.5V6a1.5 1.5 0 0 0-1.5-1.5H3.75A1.5 1.5 0 0 0 2.25 6v12a1.5 1.5 0 0 0 1.5 1.5Zm10.5-11.25h.008v.008h-.008V8.25Z"
              />
            </svg>
            <span class="mt-2 block text-xs font-semibold">Chưa có ảnh</span>
          </div>
        </div>
        <span
          class="absolute top-2.5 left-2.5 rounded-lg border px-2.5 py-1 text-[10px] font-black tracking-wider uppercase backdrop-blur-md"
          :class="
            product.is_available
              ? 'border-emerald-400/30 bg-black/70 text-emerald-400'
              : 'border-rose-400/30 bg-black/70 text-rose-400'
          "
        >
          {{ product.is_available ? "Còn hàng" : "Hết hàng" }}
        </span>
      </AppLink>
      <BaseButton
        size="sm"
        variant="secondary"
        class="absolute top-2.5 right-2.5 z-10 h-10 min-h-10 w-10 rounded-full border-white/15 bg-black/70 p-0"
        :aria-label="wishlist.has(product.id) ? 'Bỏ khỏi yêu thích' : 'Thêm vào yêu thích'"
        :title="wishlist.has(product.id) ? 'Bỏ khỏi yêu thích' : 'Thêm vào yêu thích'"
        @click="handleWishlist"
      >
        <svg
          class="h-5 w-5"
          :class="wishlist.has(product.id) ? 'fill-rose-500 text-rose-500' : 'fill-none text-white'"
          viewBox="0 0 24 24"
          stroke="currentColor"
          stroke-width="1.8"
          aria-hidden="true"
        >
          <path
            stroke-linecap="round"
            stroke-linejoin="round"
            d="M4.318 6.318a4.5 4.5 0 0 0 0 6.364L12 20.364l7.682-7.682a4.5 4.5 0 0 0-6.364-6.364L12 7.636l-1.318-1.318a4.5 4.5 0 0 0-6.364 0Z"
          />
        </svg>
      </BaseButton>
    </div>

    <div class="mt-4 flex flex-1 flex-col">
      <p class="text-xs font-semibold text-slate-400">
        {{ product.brand?.name || "Thương hiệu" }}
        <span v-if="product.category"> · {{ product.category.name }}</span>
      </p>
      <AppLink
        :to="{ name: 'product-detail', params: { slug: product.slug } }"
        class="mt-1 no-underline"
        @click="emit('select', product.id)"
      >
        <h3
          class="line-clamp-2 text-base font-black text-white transition-colors group-hover:text-emerald-400"
        >
          {{ product.name }}
        </h3>
      </AppLink>
      <div class="mt-auto flex items-end justify-between gap-3 border-t border-white/5 pt-4">
        <p class="text-sm font-black text-emerald-400">{{ priceLabel }}</p>
        <AppLink
          :to="{ name: 'product-detail', params: { slug: product.slug } }"
          class="shrink-0 rounded-full bg-white/10 px-3.5 py-1.5 text-xs font-bold text-slate-200 no-underline hover:bg-emerald-500 hover:text-black"
          @click="emit('select', product.id)"
        >
          Chi tiết
        </AppLink>
      </div>
    </div>
  </article>
</template>
