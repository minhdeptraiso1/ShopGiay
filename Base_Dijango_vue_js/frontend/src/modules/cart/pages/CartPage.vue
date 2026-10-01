<script setup lang="ts">
import { computed, onMounted, ref, watch } from "vue";
import { useRouter } from "vue-router";
import { storeToRefs } from "pinia";

import BaseButton from "@/components/base/BaseButton.vue";
import AppLink from "@/components/navigation/AppLink.vue";
import StorefrontLayout from "@/layouts/StorefrontLayout.vue";
import { useToastStore } from "@/app/stores/toast";
import { toAppError } from "@/lib/http/errors";
import { useAddresses } from "@/modules/addresses/composables/useAddresses";
import { fetchEligibleVouchers } from "@/modules/engagement/api";
import type { EligibleVoucher } from "@/modules/engagement/types";
import {
  createOrder,
  createOrderPaymentAttempt,
  generateIdempotencyKey,
  getCheckoutQuote,
} from "../api";
import { useCartStore } from "../stores/cart";
import type { CheckoutQuote, PaymentMethod } from "../types";

const router = useRouter();
const toast = useToastStore();
const cartStore = useCartStore();
const { cart, loading: cartLoading, itemCount, subtotal } = storeToRefs(cartStore);

const { addresses, loadAddresses } = useAddresses();
const selectedAddressId = ref<number | null>(null);

const quote = ref<CheckoutQuote | null>(null);
const quoteLoading = ref(false);
const quoteError = ref("");

const checkoutLoading = ref(false);
const currentIdempotencyKey = ref<string>(generateIdempotencyKey());
const selectedPaymentMethod = ref<PaymentMethod>("cod");
const appliedVoucherCode = ref("");
const eligibleVouchers = ref<EligibleVoucher[]>([]);
const loyaltyPoints = ref(0);
const voucherLoading = ref(false);

function formatCurrency(amount: string | number | null | undefined): string {
  if (amount === null || amount === undefined || amount === "") return "0 ₫";
  const num = typeof amount === "string" ? Number(amount) : amount;
  if (isNaN(num)) return "0 ₫";
  return new Intl.NumberFormat("vi-VN", { style: "currency", currency: "VND" }).format(num);
}

const defaultAddress = computed(() => {
  return addresses.value.find((a) => a.is_default) || addresses.value[0] || null;
});

async function refreshQuote(): Promise<boolean> {
  if (!selectedAddressId.value || !cart.value?.items || cart.value.items.length === 0) {
    quote.value = null;
    return false;
  }
  quoteLoading.value = true;
  quoteError.value = "";
  try {
    const itemIds = cart.value.items.map((i) => i.id);
    const result = await getCheckoutQuote({
      address_id: selectedAddressId.value,
      cart_item_ids: itemIds,
      voucher_code: appliedVoucherCode.value || undefined,
    });
    quote.value = result;
    return true;
  } catch (err) {
    quote.value = null;
    quoteError.value = toAppError(err).message;
    return false;
  } finally {
    quoteLoading.value = false;
  }
}

async function handleApplyVoucher(code: string): Promise<void> {
  appliedVoucherCode.value = code;
  if (await refreshQuote()) {
    toast.show(`Đã áp dụng mã ${code}.`, "success");
    return;
  }
  appliedVoucherCode.value = "";
}

async function handleRemoveVoucher(): Promise<void> {
  appliedVoucherCode.value = "";
  await refreshQuote();
}

async function loadEligibleVouchers(): Promise<void> {
  if (!selectedAddressId.value || !cart.value?.items.length) {
    eligibleVouchers.value = [];
    return;
  }
  voucherLoading.value = true;
  try {
    const result = await fetchEligibleVouchers({
      address_id: selectedAddressId.value,
      cart_item_ids: cart.value.items.map((item) => item.id),
    });
    loyaltyPoints.value = result.points_balance;
    eligibleVouchers.value = result.vouchers;
    if (
      appliedVoucherCode.value &&
      !result.vouchers.some((item) => item.code === appliedVoucherCode.value)
    ) {
      appliedVoucherCode.value = "";
    }
  } catch {
    eligibleVouchers.value = [];
  } finally {
    voucherLoading.value = false;
  }
}

async function handlePlaceOrder() {
  if (!selectedAddressId.value) {
    toast.show("Vui lòng chọn hoặc thêm địa chỉ nhận hàng.", "error");
    return;
  }
  if (!cart.value?.items || cart.value.items.length === 0) {
    toast.show("Giỏ hàng đang trống.", "error");
    return;
  }

  checkoutLoading.value = true;
  try {
    const itemIds = cart.value.items.map((i) => i.id);
    const order = await createOrder(
      {
        address_id: selectedAddressId.value,
        cart_item_ids: itemIds,
        payment_method: selectedPaymentMethod.value,
        voucher_code: appliedVoucherCode.value || undefined,
      },
      currentIdempotencyKey.value,
    );

    await cartStore.loadCart();

    if (selectedPaymentMethod.value === "vnpay") {
      try {
        const payment = await createOrderPaymentAttempt(order.id, generateIdempotencyKey(), {
          return_url: `${globalThis.location.origin}/orders/${String(order.id)}`,
        });
        if (payment.checkout_url) {
          globalThis.location.assign(payment.checkout_url);
          return;
        }
      } catch (err) {
        toast.show(
          `${toAppError(err).message} Đơn hàng đã được lưu, bạn có thể thử thanh toán lại.`,
          "error",
        );
      }
      await router.push(`/orders/${String(order.id)}`);
      return;
    }

    toast.show("Đặt hàng COD thành công! Đơn hàng đang chờ xác nhận.", "success");
    await router.push(`/orders/${String(order.id)}`);
  } catch (err) {
    toast.show(toAppError(err).message || "Không thể đặt hàng, vui lòng thử lại.", "error");
  } finally {
    checkoutLoading.value = false;
  }
}

onMounted(async () => {
  await Promise.all([cartStore.loadCart(), loadAddresses()]);
  if (defaultAddress.value) {
    selectedAddressId.value = defaultAddress.value.id;
  }
  await refreshQuote();
  await loadEligibleVouchers();
});

watch(
  () => addresses.value,
  (newAddresses) => {
    if (!selectedAddressId.value && newAddresses.length > 0) {
      selectedAddressId.value = defaultAddress.value?.id || newAddresses[0]?.id || null;
    }
  },
);

watch([() => selectedAddressId.value, () => cart.value?.items.length, () => subtotal.value], () => {
  void refreshQuote();
  void loadEligibleVouchers();
});
</script>

<template>
  <StorefrontLayout>
    <div class="min-h-screen pb-20 pt-8 sm:pt-12">
      <div class="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
        <!-- Breadcrumb & Header -->
        <div class="mb-8">
          <p class="text-xs font-bold uppercase tracking-widest text-emerald-400">Túi Đồ Của Bạn</p>
          <h1 class="mt-1 text-2xl sm:text-3xl font-black uppercase tracking-tight text-white">
            Giỏ Hàng ({{ itemCount }} Sản Phẩm)
          </h1>
        </div>

        <!-- Empty Cart State -->
        <div
          v-if="!cartLoading && (!cart?.items || cart.items.length === 0)"
          class="rounded-3xl border border-white/10 bg-[#12151e]/85 backdrop-blur-xl p-12 text-center text-white shadow-2xl"
        >
          <div
            class="mx-auto mb-4 flex h-16 w-16 items-center justify-center rounded-2xl bg-white/5 text-slate-400"
          >
            <svg
              class="h-8 w-8"
              fill="none"
              viewBox="0 0 24 24"
              stroke="currentColor"
              stroke-width="1.5"
            >
              <path
                stroke-linecap="round"
                stroke-linejoin="round"
                d="M16 11V7a4 4 0 00-8 0v4M5 9h14l1 12H4L5 9z"
              />
            </svg>
          </div>
          <h2 class="text-xl font-black uppercase tracking-tight">Giỏ hàng của bạn đang trống</h2>
          <p class="mt-2 text-sm text-slate-400 max-w-md mx-auto">
            Hãy khám phá ngay các mẫu giày sneaker thể thao mới nhất tại Hải Duy Shop và chọn cho
            mình đôi giày ưng ý.
          </p>
          <div class="mt-6">
            <AppLink
              to="/"
              class="inline-flex items-center gap-2 rounded-xl bg-emerald-500 px-6 py-3 text-sm font-black uppercase tracking-wider text-black no-underline hover:bg-emerald-400 transition-all shadow-lg"
            >
              Khám phá sản phẩm ngay
            </AppLink>
          </div>
        </div>

        <!-- Cart Content Grid -->
        <div v-else class="grid gap-10 lg:grid-cols-12 lg:items-start">
          <!-- Cart Items List (7 Cols) -->
          <div class="lg:col-span-7 space-y-4">
            <div
              v-for="item in cart?.items"
              :key="item.id"
              class="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4 rounded-3xl border border-white/10 bg-[#12151e]/85 backdrop-blur-xl p-4 sm:p-6 shadow-lg transition-all hover:border-white/20"
            >
              <!-- Item Image & Info -->
              <div class="flex items-center gap-4">
                <div
                  class="relative h-20 w-20 sm:h-24 sm:w-24 flex-shrink-0 overflow-hidden rounded-2xl bg-[#0c0e15] border border-white/10"
                >
                  <img
                    :src="
                      item.variant?.primary_image?.image_url ||
                      item.variant?.product?.primary_image?.image_url ||
                      'https://images.unsplash.com/photo-1542291026-7eec264c27ff?auto=format&fit=crop&w=400&q=80'
                    "
                    :alt="
                      item.variant?.product_name || item.variant?.product?.name || item.variant?.sku
                    "
                    class="h-full w-full object-cover object-center"
                  />
                </div>

                <div class="space-y-1">
                  <h3 class="text-base font-bold text-white">
                    {{
                      item.variant?.product_name || item.variant?.product?.name || item.variant?.sku
                    }}
                  </h3>
                  <div class="flex flex-wrap items-center gap-2 text-xs text-slate-400">
                    <span
                      v-if="item.variant?.size_label || item.variant?.size?.label"
                      class="font-bold text-slate-200"
                    >
                      Size: {{ item.variant?.size_label || item.variant?.size?.label }}
                    </span>
                    <span
                      v-else-if="item.variant?.option_label"
                      class="rounded bg-white/5 px-1.5 py-0.5 text-[10px] text-slate-300"
                    >
                      {{ item.variant.option_label }}
                    </span>
                    <span
                      v-if="
                        (item.variant?.size_label || item.variant?.size) &&
                        (item.variant?.color_name || item.variant?.color)
                      "
                      >•</span
                    >
                    <span
                      v-if="item.variant?.color_name || item.variant?.color?.name"
                      class="text-slate-300"
                    >
                      Màu: {{ item.variant?.color_name || item.variant?.color?.name }}
                    </span>
                    <span class="font-mono text-emerald-400/80">SKU: {{ item.variant?.sku }}</span>
                  </div>
                  <p class="text-sm font-black text-emerald-400">
                    {{ formatCurrency(item.variant?.price) }}
                  </p>
                </div>
              </div>

              <!-- Quantity Controls & Delete -->
              <div
                class="flex w-full sm:w-auto items-center justify-between sm:justify-end gap-4 pt-2 sm:pt-0 border-t sm:border-t-0 border-white/5"
              >
                <div class="flex items-center rounded-xl border border-white/15 bg-white/5 p-1">
                  <button
                    type="button"
                    class="flex h-7 w-7 items-center justify-center rounded-lg text-slate-300 hover:bg-white/10 hover:text-white cursor-pointer font-bold disabled:opacity-30"
                    :disabled="item.quantity <= 1 || cartLoading"
                    @click="cartStore.setItemQuantity(item.id, item.quantity - 1)"
                  >
                    -
                  </button>
                  <span class="w-8 text-center text-xs font-black font-mono text-white">
                    {{ item.quantity }}
                  </span>
                  <button
                    type="button"
                    class="flex h-7 w-7 items-center justify-center rounded-lg text-slate-300 hover:bg-white/10 hover:text-white cursor-pointer font-bold disabled:opacity-30"
                    :disabled="item.quantity >= 99 || cartLoading"
                    @click="cartStore.setItemQuantity(item.id, item.quantity + 1)"
                  >
                    +
                  </button>
                </div>

                <div class="text-right">
                  <div class="text-sm font-black text-white font-mono">
                    {{ formatCurrency(item.line_total) }}
                  </div>
                  <button
                    type="button"
                    class="mt-1 text-xs font-semibold text-rose-400 hover:text-rose-300 cursor-pointer"
                    :disabled="cartLoading"
                    @click="cartStore.removeItem(item.id)"
                  >
                    Xóa
                  </button>
                </div>
              </div>
            </div>
          </div>

          <!-- Checkout & Review Box (5 Cols) -->
          <div class="lg:col-span-5 space-y-6">
            <div
              class="rounded-3xl border border-white/10 bg-[#12151e]/85 backdrop-blur-xl p-6 sm:p-8 shadow-2xl space-y-6"
            >
              <h2
                class="text-lg font-black uppercase tracking-tight text-white border-b border-white/10 pb-4"
              >
                Thông Tin Thanh Toán (COD)
              </h2>

              <!-- Shipping Address Selection -->
              <div class="space-y-3">
                <div class="flex items-center justify-between">
                  <label class="text-xs font-extrabold uppercase tracking-wider text-slate-300">
                    Địa Chỉ Giao Hàng
                  </label>
                  <AppLink
                    to="/profile"
                    class="text-xs text-emerald-400 font-bold hover:underline no-underline"
                  >
                    + Thêm/Sửa địa chỉ
                  </AppLink>
                </div>

                <div
                  v-if="addresses.length === 0"
                  class="rounded-2xl border border-dashed border-white/15 p-4 text-center"
                >
                  <p class="text-xs text-slate-400">Bạn chưa có địa chỉ nhận hàng nào.</p>
                  <AppLink
                    to="/profile"
                    class="mt-2 inline-block text-xs font-bold text-emerald-400 underline"
                  >
                    Thêm địa chỉ ngay
                  </AppLink>
                </div>

                <div v-else class="space-y-2">
                  <label
                    v-for="addr in addresses"
                    :key="addr.id"
                    :class="[
                      'flex items-start gap-3 rounded-2xl border p-3.5 transition-all cursor-pointer',
                      selectedAddressId === addr.id
                        ? 'border-emerald-500/50 bg-emerald-500/10'
                        : 'border-white/10 bg-white/5 hover:border-white/20',
                    ]"
                  >
                    <input
                      type="radio"
                      name="selected-address"
                      :value="addr.id"
                      v-model="selectedAddressId"
                      class="mt-1 accent-emerald-400"
                    />
                    <div class="text-xs leading-relaxed">
                      <div class="font-bold text-white flex items-center gap-2">
                        {{ addr.recipient_name }}
                        <span
                          v-if="addr.is_default"
                          class="rounded bg-emerald-500/20 px-1.5 py-0.2 text-[10px] text-emerald-400"
                          >Mặc định</span
                        >
                      </div>
                      <p class="text-slate-400">{{ addr.phone_number }}</p>
                      <p class="text-slate-300 mt-0.5">
                        {{ addr.street_address }}, {{ addr.ward }}, {{ addr.district }},
                        {{ addr.province }}
                      </p>
                    </div>
                  </label>
                </div>
              </div>

              <!-- Voucher -->
              <div class="space-y-3 border-t border-white/10 pt-4">
                <div class="flex items-center justify-between gap-3">
                  <p class="text-xs font-black tracking-wider text-white uppercase">
                    Voucher của bạn
                  </p>
                  <p class="text-xs font-bold text-amber-300">
                    {{ loyaltyPoints.toLocaleString("vi-VN") }} điểm
                  </p>
                </div>
                <p v-if="voucherLoading" class="text-xs text-slate-400">
                  Đang tìm voucher phù hợp…
                </p>
                <div v-else-if="eligibleVouchers.length" class="space-y-2">
                  <button
                    v-for="voucher in eligibleVouchers"
                    :key="voucher.id"
                    type="button"
                    class="flex w-full items-center justify-between gap-3 rounded-xl border p-3 text-left transition"
                    :class="
                      appliedVoucherCode === voucher.code
                        ? 'border-emerald-400 bg-emerald-400/10'
                        : 'border-white/10 bg-black/20 hover:border-white/30'
                    "
                    @click="handleApplyVoucher(voucher.code)"
                  >
                    <span>
                      <span class="block font-mono text-sm font-black text-emerald-400">{{
                        voucher.code
                      }}</span>
                      <span class="mt-0.5 block text-xs text-slate-300"
                        >{{ voucher.name }} · cần
                        {{ voucher.required_points.toLocaleString("vi-VN") }} điểm</span
                      >
                    </span>
                    <span class="shrink-0 text-xs font-bold text-white"
                      >-{{ formatCurrency(voucher.discount_total) }}</span
                    >
                  </button>
                </div>
                <p v-else class="text-xs leading-relaxed text-slate-400">
                  Chưa có voucher phù hợp với điểm và giỏ hàng hiện tại.
                </p>
                <p v-if="appliedVoucherCode" class="text-xs font-bold text-emerald-400">
                  ✓ {{ appliedVoucherCode }} đang được áp dụng
                  <button type="button" class="ml-2 underline" @click="handleRemoveVoucher">
                    Bỏ chọn
                  </button>
                </p>
                <p v-else-if="quoteError" class="text-xs text-rose-400">{{ quoteError }}</p>
              </div>

              <!-- Live Quote Pricing Summary -->
              <div class="space-y-2.5 border-t border-white/10 pt-4 text-sm">
                <div class="flex items-center justify-between text-slate-300">
                  <span>Tạm tính</span>
                  <span class="font-mono font-bold text-white">{{
                    formatCurrency(quote?.subtotal || subtotal)
                  }}</span>
                </div>

                <div class="flex items-center justify-between text-slate-300">
                  <span class="flex items-center gap-1.5">
                    Phí vận chuyển
                    <span
                      v-if="Number(quote?.subtotal || subtotal) >= 1000000"
                      class="text-[10px] text-emerald-400 font-bold"
                      >(Freeship đơn từ 1Tr)</span
                    >
                  </span>
                  <span
                    class="font-mono font-bold"
                    :class="
                      Number(quote?.shipping_fee || 0) === 0 ? 'text-emerald-400' : 'text-white'
                    "
                  >
                    {{
                      Number(quote?.shipping_fee || 0) === 0
                        ? "Miễn phí"
                        : formatCurrency(quote?.shipping_fee)
                    }}
                  </span>
                </div>

                <div
                  v-if="Number(quote?.discount_total || 0) > 0"
                  class="flex items-center justify-between text-slate-300"
                >
                  <span>Giảm giá</span>
                  <span class="font-mono font-bold text-emerald-400"
                    >-{{ formatCurrency(quote?.discount_total) }}</span
                  >
                </div>

                <div
                  class="flex items-center justify-between border-t border-white/10 pt-3 text-base"
                >
                  <span class="font-black uppercase text-white">Tổng thanh toán</span>
                  <span class="font-mono text-xl font-black text-emerald-400">
                    {{ formatCurrency(quote?.total || subtotal) }}
                  </span>
                </div>
              </div>

              <!-- Payment Method -->
              <div class="space-y-2.5">
                <p class="text-xs font-black uppercase tracking-wider text-white">
                  Phương thức thanh toán
                </p>
                <div
                  class="grid gap-2 sm:grid-cols-2"
                  role="radiogroup"
                  aria-label="Phương thức thanh toán"
                >
                  <BaseButton
                    type="button"
                    variant="ghost"
                    role="radio"
                    :aria-checked="selectedPaymentMethod === 'cod'"
                    :class="[
                      'min-h-20 justify-start rounded-2xl border px-4 text-left',
                      selectedPaymentMethod === 'cod'
                        ? 'border-emerald-500/50 bg-emerald-500/10 text-white'
                        : 'border-white/10 bg-white/5 text-slate-300',
                    ]"
                    @click="selectedPaymentMethod = 'cod'"
                  >
                    <span>
                      <span class="block text-xs font-black">COD</span>
                      <span class="mt-1 block text-[11px] font-medium text-slate-400">
                        Thanh toán khi nhận hàng
                      </span>
                    </span>
                  </BaseButton>
                  <BaseButton
                    type="button"
                    variant="ghost"
                    role="radio"
                    :aria-checked="selectedPaymentMethod === 'vnpay'"
                    :class="[
                      'min-h-20 justify-start rounded-2xl border px-4 text-left',
                      selectedPaymentMethod === 'vnpay'
                        ? 'border-emerald-500/50 bg-emerald-500/10 text-white'
                        : 'border-white/10 bg-white/5 text-slate-300',
                    ]"
                    @click="selectedPaymentMethod = 'vnpay'"
                  >
                    <span>
                      <span class="block text-xs font-black">VNPAY</span>
                      <span class="mt-1 block text-[11px] font-medium text-slate-400">
                        Thanh toán trực tuyến qua sandbox
                      </span>
                    </span>
                  </BaseButton>
                </div>
              </div>

              <!-- Order Submission Button -->
              <div>
                <BaseButton
                  type="button"
                  block
                  :disabled="!selectedAddressId || !cart?.items?.length || quoteLoading"
                  :loading="checkoutLoading"
                  class="min-h-13 text-sm font-black uppercase tracking-wider rounded-2xl shadow-[0_15px_30px_rgba(16,185,129,0.35)]"
                  @click="handlePlaceOrder"
                >
                  {{
                    selectedPaymentMethod === "vnpay"
                      ? "Đặt hàng & thanh toán VNPay"
                      : "Xác nhận đặt hàng COD"
                  }}
                </BaseButton>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </StorefrontLayout>
</template>
