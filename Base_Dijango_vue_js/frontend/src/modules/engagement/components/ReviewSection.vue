<script setup lang="ts">
import { computed, onMounted, ref } from "vue";

import BaseButton from "@/components/base/BaseButton.vue";
import BaseTextarea from "@/components/base/BaseTextarea.vue";
import AppAlert from "@/components/feedback/AppAlert.vue";
import FormField from "@/components/form/FormField.vue";
import AppLink from "@/components/navigation/AppLink.vue";
import { useToastStore } from "@/app/stores/toast";
import { toAppError } from "@/lib/http/errors";
import { useAuth } from "@/modules/auth/composables/useAuth";
import { fetchMyOrders } from "@/modules/cart/api";
import type { OrderItemSnapshot } from "@/modules/cart/types";
import { createProductReview, fetchProductReviews } from "../api";
import type { Review } from "../types";

const props = defineProps<{ productId: number; productSlug: string }>();
const toast = useToastStore();
const { isAuthenticated } = useAuth();
const reviews = ref<Review[]>([]);
const eligibleItems = ref<OrderItemSnapshot[]>([]);
const loading = ref(true);
const error = ref("");
const selectedOrderItem = ref<number | null>(null);
const rating = ref(5);
const content = ref("");
const submitting = ref(false);

const average = computed(() => {
  if (!reviews.value.length) return "0.0";
  return (
    reviews.value.reduce((total, review) => total + review.rating, 0) / reviews.value.length
  ).toFixed(1);
});

async function load(): Promise<void> {
  loading.value = true;
  error.value = "";
  try {
    reviews.value = await fetchProductReviews(props.productId);
    if (isAuthenticated.value) {
      const orders = await fetchMyOrders();
      eligibleItems.value = orders
        .filter((order) => order.status === "completed")
        .flatMap((order) => order.items)
        .filter((item) => item.product_slug === props.productSlug);
      selectedOrderItem.value = eligibleItems.value[0]?.id ?? null;
    }
  } catch (err) {
    error.value = toAppError(err).message;
  } finally {
    loading.value = false;
  }
}

async function submitReview(): Promise<void> {
  if (!selectedOrderItem.value) return;
  submitting.value = true;
  try {
    await createProductReview(props.productId, {
      order_item: selectedOrderItem.value,
      rating: rating.value,
      content: content.value,
    });
    content.value = "";
    eligibleItems.value = eligibleItems.value.filter((item) => item.id !== selectedOrderItem.value);
    selectedOrderItem.value = eligibleItems.value[0]?.id ?? null;
    toast.show("Đánh giá đã được gửi và đang chờ duyệt.", "success");
  } catch (err) {
    toast.show(toAppError(err).message, "error");
  } finally {
    submitting.value = false;
  }
}

onMounted(load);
</script>

<template>
  <section
    id="reviews"
    class="mt-12 grid scroll-mt-24 gap-6 border-t border-white/10 pt-10 lg:grid-cols-[1fr_1.6fr]"
  >
    <div>
      <p class="text-xs font-black tracking-widest text-emerald-400 uppercase">Đánh giá đã mua</p>
      <h2 class="mt-2 text-3xl font-black text-white">{{ average }} / 5</h2>
      <p class="mt-1 text-sm text-slate-400">{{ reviews.length }} đánh giá đã được duyệt</p>
      <form
        v-if="isAuthenticated && eligibleItems.length"
        class="mt-6 space-y-4 rounded-2xl border border-white/10 bg-white/5 p-4"
        @submit.prevent="submitReview"
      >
        <div>
          <p class="mb-2 text-xs font-bold text-slate-300">Sản phẩm từ đơn đã hoàn tất</p>
          <div class="flex flex-wrap gap-2" role="radiogroup" aria-label="Sản phẩm đủ điều kiện">
            <BaseButton
              v-for="item in eligibleItems"
              :key="item.id"
              type="button"
              size="sm"
              :variant="selectedOrderItem === item.id ? 'primary' : 'ghost'"
              role="radio"
              :aria-checked="selectedOrderItem === item.id"
              @click="selectedOrderItem = item.id"
              >{{ item.sku }}</BaseButton
            >
          </div>
        </div>
        <div>
          <p class="mb-2 text-xs font-bold text-slate-300">Số sao</p>
          <div class="flex gap-1" role="radiogroup" aria-label="Số sao đánh giá">
            <BaseButton
              v-for="star in 5"
              :key="star"
              type="button"
              size="sm"
              variant="ghost"
              role="radio"
              :aria-checked="rating === star"
              :class="rating >= star ? 'text-amber-300' : 'text-slate-600'"
              @click="rating = star"
              >★</BaseButton
            >
          </div>
        </div>
        <FormField v-slot="field" label="Nội dung đánh giá" name="review-content" required>
          <BaseTextarea
            v-model="content"
            :id="field.id"
            name="review_content"
            placeholder="Chia sẻ trải nghiệm thực tế về sản phẩm..."
            :rows="4"
            required
          />
        </FormField>
        <BaseButton type="submit" :loading="submitting" :disabled="content.trim().length < 10"
          >Gửi đánh giá</BaseButton
        >
      </form>
      <p v-else-if="isAuthenticated" class="mt-5 text-sm text-slate-500">
        Bạn có thể đánh giá sau khi đơn chứa sản phẩm này đã hoàn tất.
      </p>
      <p v-else class="mt-5 text-sm text-slate-400">
        <AppLink to="/login" class="font-bold text-emerald-400">Đăng nhập</AppLink> để đánh giá sản
        phẩm đã mua.
      </p>
    </div>
    <div>
      <AppAlert v-if="error" variant="error" title="Không tải được đánh giá">{{ error }}</AppAlert>
      <p v-else-if="loading" class="py-8 text-center text-sm text-slate-400">Đang tải đánh giá…</p>
      <div v-else-if="reviews.length" class="space-y-3">
        <article
          v-for="review in reviews"
          :key="review.id"
          class="rounded-2xl border border-white/10 bg-[#12151e] p-5"
        >
          <div class="flex items-center justify-between gap-3">
            <p class="font-bold text-white">{{ review.user_name }}</p>
            <p class="text-amber-300" :aria-label="`${review.rating} trên 5 sao`">
              {{ "★".repeat(review.rating)
              }}<span class="text-slate-700">{{ "★".repeat(5 - review.rating) }}</span>
            </p>
          </div>
          <p class="mt-3 text-sm leading-relaxed text-slate-300">{{ review.content }}</p>
        </article>
      </div>
      <div
        v-else
        class="rounded-2xl border border-dashed border-white/15 p-8 text-center text-sm text-slate-500"
      >
        Chưa có đánh giá được duyệt cho sản phẩm này.
      </div>
    </div>
  </section>
</template>
