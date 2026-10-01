<script setup lang="ts">
import { computed, onMounted, reactive, ref } from "vue";

import { useToastStore } from "@/app/stores/toast";
import BaseButton from "@/components/base/BaseButton.vue";
import BaseInput from "@/components/base/BaseInput.vue";
import BaseTextarea from "@/components/base/BaseTextarea.vue";
import AppAlert from "@/components/feedback/AppAlert.vue";
import FormField from "@/components/form/FormField.vue";
import AdminLayout from "@/layouts/AdminLayout.vue";
import { toAppError } from "@/lib/http/errors";
import { useAuth } from "@/modules/auth/composables/useAuth";
import { fetchCategories, fetchProducts } from "@/modules/catalog/api";
import type { Category, ProductListItem } from "@/modules/catalog/types";
import {
  createAdminBanner,
  createAdminVoucher,
  deactivateAdminBanner,
  deactivateAdminVoucher,
  fetchAdminBanners,
  fetchAdminReviews,
  fetchAdminVouchers,
  moderateAdminReview,
  updateAdminBanner,
  updateAdminVoucher,
} from "../api";
import type { Banner, BannerInput, Review, Voucher, VoucherInput } from "../types";

type Tab = "reviews" | "vouchers" | "banners";
type ManagerView = "list" | "form";
interface VoucherFormState {
  code: string;
  name: string;
  discount_type: Voucher["discount_type"];
  value: string;
  max_discount: string;
  min_order_value: string;
  required_points: string;
  starts_at: string;
  ends_at: string;
  usage_limit: string;
  per_user_limit: string;
  products: number[];
  categories: number[];
  is_active: boolean;
}

interface BannerFormState {
  title: string;
  subtitle: string;
  image_url: string;
  target_url: string;
  position: Banner["position"];
  starts_at: string;
  ends_at: string;
  sort_order: string;
  is_active: boolean;
}

const toast = useToastStore();
const { user } = useAuth();
const isAdmin = computed(() => user.value?.roles.includes("ADMIN") ?? false);
const activeTab = ref<Tab>("reviews");
const loading = ref(true);
const error = ref("");
const saving = ref(false);
const reviews = ref<Review[]>([]);
const vouchers = ref<Voucher[]>([]);
const banners = ref<Banner[]>([]);
const categories = ref<Category[]>([]);
const products = ref<ProductListItem[]>([]);
const reviewFilter = ref<Review["status"] | "">("pending");
const editingVoucherId = ref<number | null>(null);
const editingBannerId = ref<number | null>(null);
const voucherView = ref<ManagerView>("list");
const bannerView = ref<ManagerView>("list");

const bannerPositionLabels: Record<Banner["position"], string> = {
  home_hero: "Hero trang chủ",
  home_strip: "Dải khuyến mãi trang chủ",
  products_top: "Đầu trang sản phẩm",
};

function localDate(offsetDays = 0): string {
  const date = new Date(Date.now() + offsetDays * 86_400_000);
  const local = new Date(date.getTime() - date.getTimezoneOffset() * 60_000);
  return local.toISOString().slice(0, 16);
}

const voucherForm = reactive<VoucherFormState>({
  code: "",
  name: "",
  discount_type: "percent",
  value: "10",
  max_discount: "100000",
  min_order_value: "0",
  required_points: "0",
  starts_at: localDate(),
  ends_at: localDate(30),
  usage_limit: "",
  per_user_limit: "1",
  products: [],
  categories: [],
  is_active: true,
});

const bannerForm = reactive<BannerFormState>({
  title: "",
  subtitle: "",
  image_url: "",
  target_url: "/products",
  position: "home_strip",
  starts_at: localDate(),
  ends_at: localDate(30),
  sort_order: "0",
  is_active: true,
});

const visibleReviews = computed(() =>
  reviewFilter.value
    ? reviews.value.filter((review) => review.status === reviewFilter.value)
    : reviews.value,
);

function toggleId(values: number[], id: number): void {
  const index = values.indexOf(id);
  if (index >= 0) values.splice(index, 1);
  else values.push(id);
}

function resetVoucher(): void {
  editingVoucherId.value = null;
  Object.assign(voucherForm, {
    code: "",
    name: "",
    discount_type: "percent",
    value: "10",
    max_discount: "100000",
    min_order_value: "0",
    required_points: "0",
    starts_at: localDate(),
    ends_at: localDate(30),
    usage_limit: "",
    per_user_limit: "1",
    products: [],
    categories: [],
    is_active: true,
  });
}

function openVoucherCreate(): void {
  resetVoucher();
  voucherView.value = "form";
}

function closeVoucherForm(): void {
  resetVoucher();
  voucherView.value = "list";
}

function editVoucher(voucher: Voucher): void {
  editingVoucherId.value = voucher.id;
  Object.assign(voucherForm, {
    ...voucher,
    max_discount: voucher.max_discount ?? "",
    usage_limit: voucher.usage_limit === null ? "" : String(voucher.usage_limit),
    per_user_limit: String(voucher.per_user_limit),
    required_points: String(voucher.required_points),
    starts_at: voucher.starts_at.slice(0, 16),
    ends_at: voucher.ends_at.slice(0, 16),
    products: [...voucher.products],
    categories: [...voucher.categories],
  });
  activeTab.value = "vouchers";
  voucherView.value = "form";
}

function resetBanner(): void {
  editingBannerId.value = null;
  Object.assign(bannerForm, {
    title: "",
    subtitle: "",
    image_url: "",
    target_url: "/products",
    position: "home_strip",
    starts_at: localDate(),
    ends_at: localDate(30),
    sort_order: "0",
    is_active: true,
  });
}

function openBannerCreate(): void {
  resetBanner();
  bannerView.value = "form";
}

function closeBannerForm(): void {
  resetBanner();
  bannerView.value = "list";
}

function editBanner(banner: Banner): void {
  editingBannerId.value = banner.id;
  Object.assign(bannerForm, {
    ...banner,
    starts_at: banner.starts_at.slice(0, 16),
    ends_at: banner.ends_at.slice(0, 16),
    sort_order: String(banner.sort_order),
  });
  activeTab.value = "banners";
  bannerView.value = "form";
}

function campaignStatus(item: { is_active: boolean; starts_at: string; ends_at: string }): {
  label: string;
  classes: string;
} {
  if (!item.is_active) return { label: "Đã tắt", classes: "bg-slate-500/15 text-slate-400" };
  const now = Date.now();
  if (new Date(item.starts_at).getTime() > now) {
    return { label: "Đã lên lịch", classes: "bg-sky-500/15 text-sky-400" };
  }
  if (new Date(item.ends_at).getTime() < now) {
    return { label: "Đã kết thúc", classes: "bg-amber-500/15 text-amber-400" };
  }
  return { label: "Đang hiển thị", classes: "bg-emerald-500/15 text-emerald-400" };
}

async function load(): Promise<void> {
  loading.value = true;
  error.value = "";
  try {
    const reviewPromise = fetchAdminReviews();
    if (isAdmin.value) {
      const [reviewData, voucherData, bannerData, categoryData, productData] = await Promise.all([
        reviewPromise,
        fetchAdminVouchers(),
        fetchAdminBanners(),
        fetchCategories(),
        fetchProducts({ page: 1 }),
      ]);
      reviews.value = reviewData;
      vouchers.value = voucherData;
      banners.value = bannerData;
      categories.value = categoryData;
      products.value = productData.results;
    } else {
      reviews.value = await reviewPromise;
    }
  } catch (err) {
    error.value = toAppError(err).message;
  } finally {
    loading.value = false;
  }
}

async function submitVoucher(): Promise<void> {
  saving.value = true;
  try {
    const payload: VoucherInput = {
      code: voucherForm.code.trim().toUpperCase(),
      name: voucherForm.name.trim(),
      discount_type: voucherForm.discount_type,
      value: voucherForm.value,
      max_discount:
        voucherForm.discount_type === "percent" && voucherForm.max_discount
          ? voucherForm.max_discount
          : null,
      min_order_value: voucherForm.min_order_value || "0",
      required_points: Number(voucherForm.required_points) || 0,
      starts_at: new Date(voucherForm.starts_at).toISOString(),
      ends_at: new Date(voucherForm.ends_at).toISOString(),
      usage_limit: voucherForm.usage_limit ? Number(voucherForm.usage_limit) : null,
      per_user_limit: Number(voucherForm.per_user_limit) || 1,
      products: voucherForm.products,
      categories: voucherForm.categories,
      is_active: voucherForm.is_active,
    };
    if (editingVoucherId.value) await updateAdminVoucher(editingVoucherId.value, payload);
    else await createAdminVoucher(payload);
    toast.show(editingVoucherId.value ? "Đã cập nhật voucher." : "Đã tạo voucher.", "success");
    resetVoucher();
    voucherView.value = "list";
    vouchers.value = await fetchAdminVouchers();
  } catch (err) {
    toast.show(toAppError(err).message, "error");
  } finally {
    saving.value = false;
  }
}

async function disableVoucher(voucher: Voucher): Promise<void> {
  try {
    await deactivateAdminVoucher(voucher.id);
    vouchers.value = await fetchAdminVouchers();
    toast.show(`Đã ngừng mã ${voucher.code}.`, "success");
  } catch (err) {
    toast.show(toAppError(err).message, "error");
  }
}

async function submitBanner(): Promise<void> {
  saving.value = true;
  try {
    const payload: BannerInput = {
      title: bannerForm.title.trim(),
      subtitle: bannerForm.subtitle.trim(),
      image_url: bannerForm.image_url.trim(),
      target_url: bannerForm.target_url.trim(),
      position: bannerForm.position,
      starts_at: new Date(bannerForm.starts_at).toISOString(),
      ends_at: new Date(bannerForm.ends_at).toISOString(),
      sort_order: Number(bannerForm.sort_order) || 0,
      is_active: bannerForm.is_active,
    };
    if (editingBannerId.value) await updateAdminBanner(editingBannerId.value, payload);
    else await createAdminBanner(payload);
    toast.show(editingBannerId.value ? "Đã cập nhật banner." : "Đã tạo banner.", "success");
    resetBanner();
    bannerView.value = "list";
    banners.value = await fetchAdminBanners();
  } catch (err) {
    toast.show(toAppError(err).message, "error");
  } finally {
    saving.value = false;
  }
}

async function disableBanner(banner: Banner): Promise<void> {
  try {
    await deactivateAdminBanner(banner.id);
    banners.value = await fetchAdminBanners();
    toast.show("Đã ngừng hiển thị banner.", "success");
  } catch (err) {
    toast.show(toAppError(err).message, "error");
  }
}

async function moderate(review: Review, status: "approved" | "rejected"): Promise<void> {
  try {
    const updated = await moderateAdminReview(review.id, status);
    const index = reviews.value.findIndex((item) => item.id === review.id);
    if (index >= 0) reviews.value[index] = updated;
    toast.show(status === "approved" ? "Đã duyệt đánh giá." : "Đã từ chối đánh giá.", "success");
  } catch (err) {
    toast.show(toAppError(err).message, "error");
  }
}

onMounted(() => void load());
</script>

<template>
  <AdminLayout>
    <div class="space-y-6">
      <header class="flex flex-wrap items-end justify-between gap-4 border-b border-white/10 pb-6">
        <div>
          <p class="text-xs font-black tracking-[0.2em] text-emerald-400 uppercase">Phase 5</p>
          <h1 class="mt-2 text-3xl font-black text-white">Tương tác & khuyến mãi</h1>
          <p class="mt-2 text-sm text-slate-400">
            Duyệt đánh giá; quản trị voucher và banner theo thời gian.
          </p>
        </div>
        <BaseButton size="sm" variant="secondary" :loading="loading" @click="load"
          >Làm mới</BaseButton
        >
      </header>

      <nav class="flex flex-wrap gap-2" aria-label="Nhóm quản trị">
        <BaseButton
          size="sm"
          :variant="activeTab === 'reviews' ? 'primary' : 'secondary'"
          @click="activeTab = 'reviews'"
        >
          Đánh giá ({{ reviews.filter((item) => item.status === "pending").length }} chờ)
        </BaseButton>
        <template v-if="isAdmin">
          <BaseButton
            size="sm"
            :variant="activeTab === 'vouchers' ? 'primary' : 'secondary'"
            @click="activeTab = 'vouchers'"
            >Voucher</BaseButton
          >
          <BaseButton
            size="sm"
            :variant="activeTab === 'banners' ? 'primary' : 'secondary'"
            @click="activeTab = 'banners'"
            >Banner</BaseButton
          >
        </template>
      </nav>

      <AppAlert v-if="error" variant="error" title="Không tải được dữ liệu">{{ error }}</AppAlert>
      <p v-else-if="loading" class="py-16 text-center text-sm text-slate-400">Đang tải dữ liệu…</p>

      <section v-else-if="activeTab === 'reviews'" class="space-y-4">
        <div class="flex flex-wrap gap-2">
          <BaseButton
            v-for="option in [
              { value: 'pending', label: 'Chờ duyệt' },
              { value: 'approved', label: 'Đã duyệt' },
              { value: 'rejected', label: 'Từ chối' },
              { value: '', label: 'Tất cả' },
            ]"
            :key="option.value"
            size="sm"
            :variant="reviewFilter === option.value ? 'primary' : 'ghost'"
            @click="reviewFilter = option.value as Review['status'] | ''"
            >{{ option.label }}</BaseButton
          >
        </div>
        <div v-if="visibleReviews.length" class="grid gap-4 xl:grid-cols-2">
          <article
            v-for="review in visibleReviews"
            :key="review.id"
            class="rounded-2xl border border-white/10 bg-[#12151e] p-5"
          >
            <div class="flex items-start justify-between gap-4">
              <div>
                <p class="font-black text-white">{{ review.product_name }}</p>
                <p class="mt-1 text-xs text-slate-500">
                  {{ review.user_name }} · {{ new Date(review.created_at).toLocaleString("vi-VN") }}
                </p>
              </div>
              <span class="text-amber-300">{{ "★".repeat(review.rating) }}</span>
            </div>
            <p class="mt-4 text-sm leading-6 text-slate-300">{{ review.content }}</p>
            <div
              v-if="review.status === 'pending'"
              class="mt-5 flex gap-2 border-t border-white/10 pt-4"
            >
              <BaseButton size="sm" @click="moderate(review, 'approved')">Duyệt</BaseButton>
              <BaseButton size="sm" variant="danger" @click="moderate(review, 'rejected')"
                >Từ chối</BaseButton
              >
            </div>
            <p
              v-else
              class="mt-4 text-xs font-bold uppercase"
              :class="review.status === 'approved' ? 'text-emerald-400' : 'text-rose-400'"
            >
              {{ review.status === "approved" ? "Đã duyệt" : "Đã từ chối" }}
            </p>
          </article>
        </div>
        <div
          v-else
          class="rounded-2xl border border-dashed border-white/15 p-12 text-center text-slate-500"
        >
          Không có đánh giá trong nhóm này.
        </div>
      </section>

      <section v-else-if="activeTab === 'vouchers' && isAdmin" class="space-y-5">
        <div
          class="flex flex-wrap items-center justify-between gap-4 rounded-2xl border border-white/10 bg-[#12151e] p-5"
        >
          <div>
            <p class="text-xs font-black tracking-widest text-emerald-400 uppercase">Khuyến mãi</p>
            <h2 class="mt-1 text-xl font-black text-white">
              {{
                voucherView === "list"
                  ? "Danh sách voucher"
                  : editingVoucherId
                    ? "Chỉnh sửa voucher"
                    : "Tạo voucher mới"
              }}
            </h2>
            <p class="mt-1 text-sm text-slate-400">
              {{
                voucherView === "list"
                  ? `${vouchers.length} chương trình · ${vouchers.filter((item) => campaignStatus(item).label === "Đang hiển thị").length} đang áp dụng`
                  : "Thiết lập giá trị, thời gian, giới hạn và phạm vi áp dụng."
              }}
            </p>
          </div>
          <BaseButton v-if="voucherView === 'list'" @click="openVoucherCreate"
            >+ Thêm voucher</BaseButton
          >
          <BaseButton v-else variant="secondary" @click="closeVoucherForm"
            >← Danh sách voucher</BaseButton
          >
        </div>

        <div v-if="voucherView === 'list'" class="grid gap-4 md:grid-cols-2 xl:grid-cols-3">
          <article
            v-for="voucher in vouchers"
            :key="voucher.id"
            class="rounded-2xl border border-white/10 bg-[#12151e] p-5"
          >
            <div class="flex items-start justify-between gap-3">
              <div>
                <p class="font-mono text-xl font-black text-emerald-400">{{ voucher.code }}</p>
                <p class="mt-1 font-bold text-white">{{ voucher.name }}</p>
              </div>
              <span
                class="rounded-full px-2.5 py-1 text-[10px] font-black uppercase"
                :class="campaignStatus(voucher).classes"
              >
                {{ campaignStatus(voucher).label }}
              </span>
            </div>
            <div class="mt-5 grid grid-cols-2 gap-3 text-xs">
              <div class="rounded-xl bg-white/5 p-3">
                <p class="text-slate-500">Mức giảm</p>
                <p class="mt-1 font-black text-white">
                  {{
                    voucher.discount_type === "percent"
                      ? `${voucher.value}%`
                      : `${Number(voucher.value).toLocaleString("vi-VN")} đ`
                  }}
                </p>
              </div>
              <div class="rounded-xl bg-white/5 p-3">
                <p class="text-slate-500">Lượt sử dụng</p>
                <p class="mt-1 font-black text-white">
                  {{ voucher.usage_count
                  }}{{ voucher.usage_limit ? ` / ${voucher.usage_limit}` : "" }}
                </p>
              </div>
            </div>
            <p class="mt-4 text-xs text-slate-500">
              Điểm tối thiểu: {{ voucher.required_points.toLocaleString("vi-VN") }} ·
              {{ new Date(voucher.starts_at).toLocaleDateString("vi-VN") }} →
              {{ new Date(voucher.ends_at).toLocaleDateString("vi-VN") }}
            </p>
            <div class="mt-4 flex gap-2 border-t border-white/10 pt-4">
              <BaseButton size="sm" variant="secondary" @click="editVoucher(voucher)"
                >Chỉnh sửa</BaseButton
              >
              <BaseButton
                v-if="voucher.is_active"
                size="sm"
                variant="danger"
                @click="disableVoucher(voucher)"
                >Ngừng</BaseButton
              >
            </div>
          </article>
          <button
            v-if="!vouchers.length"
            type="button"
            class="min-h-52 rounded-2xl border border-dashed border-white/15 p-8 text-center text-sm text-slate-500 hover:border-emerald-500/40 hover:text-emerald-400"
            @click="openVoucherCreate"
          >
            Chưa có voucher. Nhấn để tạo chương trình đầu tiên.
          </button>
        </div>

        <form
          v-else
          class="mx-auto max-w-5xl space-y-6 rounded-3xl border border-white/10 bg-[#12151e] p-5 sm:p-7"
          @submit.prevent="submitVoucher"
        >
          <div class="grid gap-4 sm:grid-cols-2">
            <FormField v-slot="field" label="Mã voucher" name="voucher-code" required
              ><BaseInput
                v-model="voucherForm.code"
                :id="field.id"
                name="code"
                required
                class="uppercase"
                placeholder="VD: SALE10"
            /></FormField>
            <FormField v-slot="field" label="Tên chương trình" name="voucher-name" required
              ><BaseInput
                v-model="voucherForm.name"
                :id="field.id"
                name="name"
                required
                placeholder="Ưu đãi khách hàng mới"
            /></FormField>
          </div>
          <div
            class="grid gap-4 rounded-2xl border border-white/10 p-4 sm:grid-cols-2 lg:grid-cols-4"
          >
            <div>
              <p class="mb-2 text-xs font-bold text-slate-300">Loại giảm</p>
              <div class="flex gap-2">
                <BaseButton
                  size="sm"
                  type="button"
                  :variant="voucherForm.discount_type === 'percent' ? 'primary' : 'secondary'"
                  @click="voucherForm.discount_type = 'percent'"
                  >Phần trăm</BaseButton
                ><BaseButton
                  size="sm"
                  type="button"
                  :variant="voucherForm.discount_type === 'fixed' ? 'primary' : 'secondary'"
                  @click="voucherForm.discount_type = 'fixed'"
                  >Số tiền</BaseButton
                >
              </div>
            </div>
            <FormField v-slot="field" label="Giá trị giảm" name="voucher-value" required
              ><BaseInput
                v-model="voucherForm.value"
                :id="field.id"
                name="value"
                type="number"
                required
            /></FormField>
            <FormField v-slot="field" label="Giảm tối đa" name="voucher-max"
              ><BaseInput
                v-model="voucherForm.max_discount"
                :id="field.id"
                name="max_discount"
                type="number"
                :disabled="voucherForm.discount_type === 'fixed'"
            /></FormField>
            <FormField v-slot="field" label="Đơn tối thiểu" name="voucher-min"
              ><BaseInput
                v-model="voucherForm.min_order_value"
                :id="field.id"
                name="min_order"
                type="number"
            /></FormField>
            <FormField
              v-slot="field"
              label="Điểm tối thiểu"
              name="voucher-required-points"
              hint="Khách chỉ cần đạt mức điểm này; áp voucher không trừ điểm."
            >
              <BaseInput
                v-model="voucherForm.required_points"
                :id="field.id"
                name="required_points"
                type="number"
                min="0"
              />
            </FormField>
          </div>
          <div class="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
            <FormField v-slot="field" label="Bắt đầu" name="voucher-start" required
              ><BaseInput
                v-model="voucherForm.starts_at"
                :id="field.id"
                name="starts_at"
                type="datetime-local"
                required
            /></FormField>
            <FormField v-slot="field" label="Kết thúc" name="voucher-end" required
              ><BaseInput
                v-model="voucherForm.ends_at"
                :id="field.id"
                name="ends_at"
                type="datetime-local"
                required
            /></FormField>
            <FormField v-slot="field" label="Tổng lượt dùng" name="voucher-limit"
              ><BaseInput
                v-model="voucherForm.usage_limit"
                :id="field.id"
                name="usage_limit"
                type="number"
                placeholder="Không giới hạn"
            /></FormField>
            <FormField v-slot="field" label="Lượt dùng / khách" name="voucher-user-limit"
              ><BaseInput
                v-model="voucherForm.per_user_limit"
                :id="field.id"
                name="per_user_limit"
                type="number"
            /></FormField>
          </div>
          <fieldset>
            <legend class="text-xs font-bold text-slate-300">
              Danh mục áp dụng <span class="font-normal text-slate-500">(bỏ trống = toàn bộ)</span>
            </legend>
            <div class="mt-3 flex flex-wrap gap-2">
              <BaseButton
                v-for="category in categories"
                :key="category.id"
                type="button"
                size="sm"
                :variant="voucherForm.categories.includes(category.id) ? 'primary' : 'ghost'"
                @click="toggleId(voucherForm.categories, category.id)"
                >{{ category.name }}</BaseButton
              >
            </div>
          </fieldset>
          <fieldset>
            <legend class="text-xs font-bold text-slate-300">
              Sản phẩm áp dụng <span class="font-normal text-slate-500">(bỏ trống = toàn bộ)</span>
            </legend>
            <div
              class="mt-3 grid max-h-52 gap-1 overflow-y-auto rounded-xl border border-white/10 p-2 sm:grid-cols-2"
            >
              <label
                v-for="product in products"
                :key="product.id"
                class="flex cursor-pointer items-center gap-2 rounded-lg px-3 py-2 text-xs text-slate-300 hover:bg-white/5"
                ><input
                  type="checkbox"
                  :checked="voucherForm.products.includes(product.id)"
                  class="accent-emerald-500"
                  @change="toggleId(voucherForm.products, product.id)"
                />{{ product.name }}</label
              >
            </div>
          </fieldset>
          <div
            class="flex flex-wrap items-center justify-between gap-4 border-t border-white/10 pt-5"
          >
            <label class="flex items-center gap-2 text-sm text-slate-300"
              ><input
                v-model="voucherForm.is_active"
                type="checkbox"
                class="accent-emerald-500"
              />Kích hoạt chương trình</label
            >
            <div class="flex gap-2">
              <BaseButton type="button" variant="ghost" @click="closeVoucherForm">Hủy</BaseButton
              ><BaseButton type="submit" :loading="saving">{{
                editingVoucherId ? "Lưu thay đổi" : "Tạo voucher"
              }}</BaseButton>
            </div>
          </div>
        </form>
      </section>

      <section v-else-if="activeTab === 'banners' && isAdmin" class="space-y-5">
        <div
          class="flex flex-wrap items-center justify-between gap-4 rounded-2xl border border-white/10 bg-[#12151e] p-5"
        >
          <div>
            <p class="text-xs font-black tracking-widest text-emerald-400 uppercase">
              Khu vực quảng bá
            </p>
            <h2 class="mt-1 text-xl font-black text-white">
              {{
                bannerView === "list"
                  ? "Lịch đăng banner"
                  : editingBannerId
                    ? "Chỉnh sửa banner"
                    : "Đăng banner mới"
              }}
            </h2>
            <p class="mt-1 text-sm text-slate-400">
              Quản lý hình ảnh theo vị trí và thời gian xuất hiện trên cửa hàng.
            </p>
          </div>
          <BaseButton v-if="bannerView === 'list'" @click="openBannerCreate"
            >+ Đăng banner</BaseButton
          >
          <BaseButton v-else variant="secondary" @click="closeBannerForm">← Lịch đăng</BaseButton>
        </div>

        <div v-if="bannerView === 'list'" class="grid gap-5 lg:grid-cols-2">
          <article
            v-for="banner in banners"
            :key="banner.id"
            class="overflow-hidden rounded-2xl border border-white/10 bg-[#12151e]"
          >
            <div class="relative aspect-[16/6] bg-white/5">
              <img
                :src="banner.image_url"
                :alt="banner.title"
                class="h-full w-full object-cover"
              /><span
                class="absolute top-3 right-3 rounded-full px-2.5 py-1 text-[10px] font-black uppercase backdrop-blur"
                :class="campaignStatus(banner).classes"
                >{{ campaignStatus(banner).label }}</span
              >
            </div>
            <div class="p-5">
              <p class="text-xs font-black tracking-wider text-emerald-400 uppercase">
                {{ bannerPositionLabels[banner.position] }}
              </p>
              <h3 class="mt-1 text-lg font-black text-white">{{ banner.title }}</h3>
              <p class="mt-1 line-clamp-2 text-sm text-slate-400">
                {{ banner.subtitle || "Không có mô tả" }}
              </p>
              <div
                class="mt-4 flex flex-wrap items-center justify-between gap-3 border-t border-white/10 pt-4"
              >
                <p class="text-xs text-slate-500">
                  {{ new Date(banner.starts_at).toLocaleString("vi-VN") }} →
                  {{ new Date(banner.ends_at).toLocaleString("vi-VN") }}
                </p>
                <div class="flex gap-2">
                  <BaseButton size="sm" variant="secondary" @click="editBanner(banner)"
                    >Chỉnh sửa</BaseButton
                  ><BaseButton
                    v-if="banner.is_active"
                    size="sm"
                    variant="danger"
                    @click="disableBanner(banner)"
                    >Ngừng</BaseButton
                  >
                </div>
              </div>
            </div>
          </article>
          <button
            v-if="!banners.length"
            type="button"
            class="min-h-64 rounded-2xl border border-dashed border-white/15 p-8 text-center text-sm text-slate-500 hover:border-emerald-500/40 hover:text-emerald-400"
            @click="openBannerCreate"
          >
            Chưa có banner. Nhấn để đăng nội dung đầu tiên.
          </button>
        </div>

        <div v-else class="grid gap-6 xl:grid-cols-[minmax(0,1fr)_22rem]">
          <form
            class="grid gap-4 rounded-3xl border border-white/10 bg-[#12151e] p-5 sm:grid-cols-2 sm:p-7"
            @submit.prevent="submitBanner"
          >
            <FormField v-slot="field" label="Tiêu đề" name="banner-title" required
              ><BaseInput
                v-model="bannerForm.title"
                :id="field.id"
                name="title"
                required
                placeholder="Thông điệp chính"
            /></FormField>
            <FormField v-slot="field" label="URL ảnh" name="banner-image" required
              ><BaseInput
                v-model="bannerForm.image_url"
                :id="field.id"
                name="image_url"
                type="url"
                required
                placeholder="https://..."
            /></FormField>
            <FormField
              v-slot="field"
              class="sm:col-span-2"
              label="Mô tả ngắn"
              name="banner-subtitle"
              ><BaseTextarea v-model="bannerForm.subtitle" :id="field.id" name="subtitle" :rows="3"
            /></FormField>
            <FormField v-slot="field" label="Liên kết khi bấm" name="banner-target"
              ><BaseInput
                v-model="bannerForm.target_url"
                :id="field.id"
                name="target_url"
                placeholder="/products"
            /></FormField>
            <div>
              <p class="mb-2 text-xs font-bold text-slate-300">Vị trí hiển thị</p>
              <div class="flex flex-wrap gap-2">
                <BaseButton
                  v-for="position in [
                    { value: 'home_strip', label: 'Dải trang chủ' },
                    { value: 'products_top', label: 'Trang sản phẩm' },
                  ]"
                  :key="position.value"
                  type="button"
                  size="sm"
                  :variant="bannerForm.position === position.value ? 'primary' : 'secondary'"
                  @click="bannerForm.position = position.value as Banner['position']"
                  >{{ position.label }}</BaseButton
                >
              </div>
            </div>
            <FormField v-slot="field" label="Bắt đầu hiển thị" name="banner-start" required
              ><BaseInput
                v-model="bannerForm.starts_at"
                :id="field.id"
                name="starts_at"
                type="datetime-local"
                required
            /></FormField>
            <FormField v-slot="field" label="Kết thúc hiển thị" name="banner-end" required
              ><BaseInput
                v-model="bannerForm.ends_at"
                :id="field.id"
                name="ends_at"
                type="datetime-local"
                required
            /></FormField>
            <FormField v-slot="field" label="Độ ưu tiên" name="banner-order"
              ><BaseInput
                v-model="bannerForm.sort_order"
                :id="field.id"
                name="sort_order"
                type="number"
            /></FormField>
            <label class="flex items-center gap-2 self-end pb-3 text-sm text-slate-300"
              ><input
                v-model="bannerForm.is_active"
                type="checkbox"
                class="accent-emerald-500"
              />Cho phép hiển thị</label
            >
            <div class="flex justify-end gap-2 border-t border-white/10 pt-5 sm:col-span-2">
              <BaseButton type="button" variant="ghost" @click="closeBannerForm">Hủy</BaseButton
              ><BaseButton type="submit" :loading="saving">{{
                editingBannerId ? "Lưu thay đổi" : "Lên lịch đăng"
              }}</BaseButton>
            </div>
          </form>
          <aside
            class="h-fit rounded-3xl border border-white/10 bg-[#12151e] p-5 xl:sticky xl:top-5"
          >
            <p class="text-xs font-black tracking-widest text-slate-400 uppercase">Xem trước</p>
            <div class="mt-4 overflow-hidden rounded-2xl border border-white/10 bg-[#080a0f]">
              <div class="aspect-[16/7] bg-white/5">
                <img
                  v-if="bannerForm.image_url"
                  :src="bannerForm.image_url"
                  alt="Xem trước banner"
                  class="h-full w-full object-cover"
                />
                <div v-else class="flex h-full items-center justify-center text-xs text-slate-600">
                  Ảnh banner sẽ xuất hiện tại đây
                </div>
              </div>
              <div class="p-4">
                <p class="font-black text-white">{{ bannerForm.title || "Tiêu đề banner" }}</p>
                <p class="mt-1 text-xs text-slate-400">
                  {{ bannerForm.subtitle || "Mô tả ngắn cho chiến dịch" }}
                </p>
              </div>
            </div>
            <div class="mt-4 space-y-2 text-xs text-slate-400">
              <p>
                <span class="text-slate-500">Vị trí:</span>
                {{ bannerPositionLabels[bannerForm.position] }}
              </p>
              <p>
                <span class="text-slate-500">Điều hướng:</span>
                {{ bannerForm.target_url || "Không có" }}
              </p>
            </div>
          </aside>
        </div>
      </section>
    </div>
  </AdminLayout>
</template>
