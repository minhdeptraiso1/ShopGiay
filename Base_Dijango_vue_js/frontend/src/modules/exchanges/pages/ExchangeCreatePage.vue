<script setup lang="ts">
import { computed, onMounted, reactive, ref } from "vue";
import { useRoute, useRouter } from "vue-router";

import { useToastStore } from "@/app/stores/toast";
import BaseButton from "@/components/base/BaseButton.vue";
import BaseInput from "@/components/base/BaseInput.vue";
import BaseTextarea from "@/components/base/BaseTextarea.vue";
import AppAlert from "@/components/feedback/AppAlert.vue";
import FormField from "@/components/form/FormField.vue";
import AppLink from "@/components/navigation/AppLink.vue";
import StorefrontLayout from "@/layouts/StorefrontLayout.vue";
import { toAppError } from "@/lib/http/errors";
import { fetchOrderDetail } from "@/modules/cart/api";
import type { Order, OrderItemSnapshot } from "@/modules/cart/types";
import { fetchProductDetail } from "@/modules/catalog/api";
import type { ProductVariant } from "@/modules/catalog/types";
import { createExchange } from "../api";

interface ExchangeRow {
  item: OrderItemSnapshot;
  variants: ProductVariant[];
  selected: boolean;
  targetVariantId: number | null;
  quantity: string;
}

const route = useRoute();
const router = useRouter();
const toast = useToastStore();
const order = ref<Order | null>(null);
const rows = reactive<ExchangeRow[]>([]);
const loading = ref(true);
const submitting = ref(false);
const error = ref("");
const reason = ref("Sai kích cỡ");
const evidenceUrl = ref("");
const customerNote = ref("");
const orderId = computed(() => Number(route.query.order));
const selectedRows = computed(() => rows.filter((row) => row.selected));

async function load(): Promise<void> {
  if (!Number.isInteger(orderId.value)) {
    error.value = "Thiếu mã đơn hàng cần đổi.";
    loading.value = false;
    return;
  }
  try {
    order.value = await fetchOrderDetail(orderId.value);
    if (order.value.status !== "completed") {
      error.value = "Chỉ đơn hàng đã hoàn tất mới được yêu cầu đổi.";
      return;
    }
    const products = await Promise.all(
      order.value.items.map((item) => fetchProductDetail(item.product_slug)),
    );
    order.value.items.forEach((item, index) => {
      rows.push({
        item,
        variants: (products[index]?.variants ?? []).filter(
          (variant) => variant.id !== item.variant && variant.is_available,
        ),
        selected: false,
        targetVariantId: null,
        quantity: "1",
      });
    });
  } catch (err) {
    error.value = toAppError(err).message;
  } finally {
    loading.value = false;
  }
}

async function submit(): Promise<void> {
  if (!selectedRows.value.length) {
    toast.show("Hãy chọn ít nhất một sản phẩm cần đổi.", "error");
    return;
  }
  if (selectedRows.value.some((row) => !row.targetVariantId)) {
    toast.show("Hãy chọn size/màu thay thế cho tất cả sản phẩm.", "error");
    return;
  }
  submitting.value = true;
  try {
    await createExchange(
      {
        order_id: orderId.value,
        reason: reason.value,
        evidence_url: evidenceUrl.value.trim() || undefined,
        customer_note: customerNote.value.trim() || undefined,
        items: selectedRows.value.map((row) => ({
          order_item_id: row.item.id,
          target_variant_id: row.targetVariantId ?? 0,
          quantity: Math.min(row.item.quantity, Math.max(1, Number(row.quantity) || 1)),
        })),
      },
      globalThis.crypto.randomUUID(),
    );
    toast.show("Đã gửi yêu cầu đổi hàng.", "success");
    await router.push({ name: "exchanges" });
  } catch (err) {
    toast.show(toAppError(err).message, "error");
  } finally {
    submitting.value = false;
  }
}

onMounted(() => void load());
</script>

<template>
  <StorefrontLayout>
    <main class="mx-auto min-h-[70vh] max-w-5xl px-4 py-10 sm:px-6 lg:px-8">
      <AppLink
        to="/orders"
        class="text-xs font-bold text-slate-400 no-underline hover:text-emerald-400"
        >← Đơn hàng của tôi</AppLink
      >
      <div class="mt-5 border-b border-white/10 pb-6">
        <p class="text-xs font-black tracking-[0.2em] text-emerald-400 uppercase">Đổi size / màu</p>
        <h1 class="mt-2 text-3xl font-black text-white">Yêu cầu đổi hàng</h1>
        <p class="mt-2 text-sm text-slate-400">
          Chỉ đổi sang biến thể khác trong cùng sản phẩm. Không phát sinh hoàn tiền hoặc chênh lệch
          giá.
        </p>
      </div>

      <p v-if="loading" class="py-16 text-center text-slate-400">Đang tải sản phẩm đủ điều kiện…</p>
      <AppAlert v-else-if="error" class="mt-6" variant="error" title="Không thể tạo yêu cầu">{{
        error
      }}</AppAlert>
      <form v-else-if="order" class="mt-6 space-y-6" @submit.prevent="submit">
        <section class="space-y-3">
          <article
            v-for="row in rows"
            :key="row.item.id"
            class="rounded-2xl border border-white/10 bg-[#12151e] p-5"
          >
            <label class="flex cursor-pointer items-start gap-3">
              <input
                v-model="row.selected"
                type="checkbox"
                class="mt-1 h-4 w-4 accent-emerald-500"
                :disabled="!row.variants.length"
              />
              <span
                ><span class="block font-black text-white">{{ row.item.product_name }}</span
                ><span class="mt-1 block text-xs text-slate-400"
                  >Hiện tại: {{ row.item.size_label }} · {{ row.item.color_name }} ·
                  {{ row.item.sku }}</span
                ></span
              >
            </label>
            <p v-if="!row.variants.length" class="mt-3 text-xs text-amber-400">
              Hiện chưa có biến thể khác còn hàng.
            </p>
            <div
              v-else-if="row.selected"
              class="mt-5 grid gap-4 border-t border-white/10 pt-4 md:grid-cols-[1fr_9rem]"
            >
              <fieldset>
                <legend class="mb-2 text-xs font-bold text-slate-300">
                  Chọn size/màu thay thế
                </legend>
                <div class="flex flex-wrap gap-2">
                  <BaseButton
                    v-for="variant in row.variants"
                    :key="variant.id"
                    type="button"
                    size="sm"
                    :variant="row.targetVariantId === variant.id ? 'primary' : 'secondary'"
                    @click="row.targetVariantId = variant.id"
                    >{{ variant.size?.label || "Free" }} ·
                    {{ variant.color?.name || "Mặc định" }}</BaseButton
                  >
                </div>
              </fieldset>
              <FormField v-slot="field" label="Số lượng" :name="`quantity-${row.item.id}`"
                ><BaseInput
                  v-model="row.quantity"
                  :id="field.id"
                  :name="`quantity_${row.item.id}`"
                  type="number"
                  min="1"
                  :max="row.item.quantity"
              /></FormField>
            </div>
          </article>
        </section>

        <section
          class="grid gap-5 rounded-3xl border border-white/10 bg-white/[0.03] p-5 md:grid-cols-2"
        >
          <div class="md:col-span-2">
            <p class="mb-2 text-xs font-bold text-slate-300">Lý do đổi</p>
            <div class="flex flex-wrap gap-2">
              <BaseButton
                v-for="option in [
                  'Sai kích cỡ',
                  'Muốn đổi màu',
                  'Shop giao sai biến thể',
                  'Sản phẩm có lỗi',
                ]"
                :key="option"
                type="button"
                size="sm"
                :variant="reason === option ? 'primary' : 'secondary'"
                @click="reason = option"
                >{{ option }}</BaseButton
              >
            </div>
          </div>
          <FormField v-slot="field" label="URL ảnh bằng chứng (nếu có)" name="evidence-url"
            ><BaseInput
              v-model="evidenceUrl"
              :id="field.id"
              name="evidence_url"
              type="url"
              placeholder="https://..."
          /></FormField>
          <FormField v-slot="field" label="Ghi chú" name="customer-note"
            ><BaseTextarea
              v-model="customerNote"
              :id="field.id"
              name="customer_note"
              :rows="3"
              placeholder="Mô tả tình trạng sản phẩm, tem và hộp…"
          /></FormField>
        </section>
        <div class="flex justify-end gap-3">
          <AppLink
            to="/orders"
            class="inline-flex min-h-12 items-center rounded-xl px-5 text-sm font-bold text-slate-300 no-underline hover:bg-white/5"
            >Hủy</AppLink
          ><BaseButton type="submit" :loading="submitting">Gửi yêu cầu đổi</BaseButton>
        </div>
      </form>
    </main>
  </StorefrontLayout>
</template>
