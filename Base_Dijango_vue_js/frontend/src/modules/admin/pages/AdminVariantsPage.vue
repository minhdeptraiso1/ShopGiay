<script setup lang="ts">
import { computed, onMounted, reactive, ref, watch } from "vue";
import { useRoute } from "vue-router";

import BaseButton from "@/components/base/BaseButton.vue";
import BaseInput from "@/components/base/BaseInput.vue";
import AppAlert from "@/components/feedback/AppAlert.vue";
import AppPopup from "@/components/feedback/AppPopup.vue";
import FormField from "@/components/form/FormField.vue";
import AppLink from "@/components/navigation/AppLink.vue";
import AdminLayout from "@/layouts/AdminLayout.vue";
import { useToastStore } from "@/app/stores/toast";
import { toAppError } from "@/lib/http/errors";
import {
  createAdminVariant,
  deleteAdminVariant,
  fetchAdminColors,
  fetchAdminProducts,
  fetchAdminSizes,
  fetchAdminVariants,
  updateAdminVariant,
  type AdminColor,
  type AdminProduct,
  type AdminSize,
  type AdminVariant,
  type CreateVariantInput,
} from "../api";

const toast = useToastStore();
const route = useRoute();
const variants = ref<AdminVariant[]>([]);
const products = ref<AdminProduct[]>([]);
const sizes = ref<AdminSize[]>([]);
const colors = ref<AdminColor[]>([]);
const loading = ref(true);
const error = ref("");
const selectedProductFilter = ref<number | "">("");

// Modal Create / Edit state
const showModal = ref(false);
const isEditing = ref(false);
const editingVariantId = ref<number | null>(null);
const submitting = ref(false);
const formError = ref("");

const formData = reactive<{
  product: number | "";
  size: number | "";
  color: number | "";
  option_label: string;
  sku: string;
  price: string;
  low_stock_threshold: number;
  is_active: boolean;
}>({
  product: "",
  size: "",
  color: "",
  option_label: "",
  sku: "",
  price: "1500000",
  low_stock_threshold: 5,
  is_active: true,
});

// Delete Confirmation
const showDeleteConfirm = ref(false);
const variantToDelete = ref<AdminVariant | null>(null);
const deleteLoading = ref(false);

const filteredVariants = computed(() => {
  if (!selectedProductFilter.value) return variants.value;
  return variants.value.filter((v) => v.product === Number(selectedProductFilter.value));
});

// Filter sizes that match the selected product's brand
const availableSizes = computed(() => {
  if (!formData.product) return sizes.value;
  const prod = products.value.find((p) => p.id === Number(formData.product));
  if (!prod) return sizes.value;
  return sizes.value.filter((s) => s.brand === prod.brand);
});

async function loadData() {
  loading.value = true;
  error.value = "";
  try {
    const [variantsRes, productsRes, sizesRes, colorsRes] = await Promise.all([
      fetchAdminVariants(),
      fetchAdminProducts(),
      fetchAdminSizes(),
      fetchAdminColors(),
    ]);
    variants.value = variantsRes;
    products.value = productsRes;
    sizes.value = sizesRes;
    colors.value = colorsRes;
    const requestedProductId = Number(route.query.product);
    if (
      Number.isInteger(requestedProductId) &&
      products.value.some((product) => product.id === requestedProductId)
    ) {
      selectedProductFilter.value = requestedProductId;
      if (route.query.create === "1") openCreateModal(requestedProductId);
    } else if (route.query.create === "1") {
      openCreateModal();
    }
  } catch (err) {
    error.value = toAppError(err).message;
  } finally {
    loading.value = false;
  }
}

function autoGenerateSku() {
  if (isEditing.value) return;
  const prod = products.value.find((p) => p.id === Number(formData.product));
  const sz = sizes.value.find((s) => s.id === Number(formData.size));
  const clr = colors.value.find((c) => c.id === Number(formData.color));

  const parts: string[] = [];
  if (prod) parts.push(prod.slug.toUpperCase().slice(0, 8));
  if (sz) parts.push(`SZ${sz.label}`);
  if (clr) parts.push(clr.slug.toUpperCase().slice(0, 4));

  if (parts.length > 0) {
    formData.sku = parts.join("-");
  }
}

watch(
  () => [formData.product, formData.size, formData.color],
  () => {
    autoGenerateSku();
  },
);

function openCreateModal(productId?: number) {
  isEditing.value = false;
  editingVariantId.value = null;
  formError.value = "";
  formData.product = productId ?? (products.value.length > 0 ? (products.value[0]?.id ?? "") : "");
  formData.size = "";
  formData.color = "";
  formData.option_label = "";
  formData.sku = "";
  formData.price = "1500000";
  formData.low_stock_threshold = 5;
  formData.is_active = true;
  showModal.value = true;
  autoGenerateSku();
}

function openEditModal(variant: AdminVariant) {
  isEditing.value = true;
  editingVariantId.value = variant.id;
  formError.value = "";
  formData.product = variant.product;
  formData.size = variant.size ?? "";
  formData.color = variant.color ?? "";
  formData.option_label = variant.option_label;
  formData.sku = variant.sku;
  formData.price = String(Math.round(Number(variant.price)));
  formData.low_stock_threshold = variant.low_stock_threshold;
  formData.is_active = variant.is_active;
  showModal.value = true;
}

async function handleFormSubmit() {
  if (!formData.product) {
    formError.value = "Vui lòng chọn sản phẩm.";
    return;
  }
  if (!formData.sku.trim()) {
    formError.value = "Mã SKU không được để trống.";
    return;
  }
  if (!formData.price || Number(formData.price) <= 0) {
    formError.value = "Giá bán phải lớn hơn 0.";
    return;
  }

  submitting.value = true;
  formError.value = "";

  try {
    if (isEditing.value && editingVariantId.value) {
      const updated = await updateAdminVariant(editingVariantId.value, {
        product: formData.product,
        size: formData.size || null,
        color: formData.color || null,
        option_label: formData.option_label.trim(),
        sku: formData.sku.trim().toUpperCase(),
        price: formData.price,
        low_stock_threshold: formData.low_stock_threshold,
        is_active: formData.is_active,
      });
      const idx = variants.value.findIndex((v) => v.id === updated.id);
      if (idx !== -1) variants.value[idx] = updated;
      toast.show("Cập nhật biến thể thành công!", "success");
    } else {
      const payload: CreateVariantInput = {
        product: formData.product,
        size: formData.size || null,
        color: formData.color || null,
        option_label: formData.option_label.trim(),
        sku: formData.sku.trim().toUpperCase(),
        price: formData.price,
        currency: "VND",
        low_stock_threshold: formData.low_stock_threshold,
        is_active: formData.is_active,
      };
      const created = await createAdminVariant(payload);
      variants.value.unshift(created);
      toast.show("Tạo biến thể mới thành công!", "success");
    }
    showModal.value = false;
  } catch (err) {
    formError.value = toAppError(err).message;
  } finally {
    submitting.value = false;
  }
}

function confirmDelete(variant: AdminVariant) {
  variantToDelete.value = variant;
  showDeleteConfirm.value = true;
}

async function handleDelete() {
  if (!variantToDelete.value) return;
  deleteLoading.value = true;
  try {
    await deleteAdminVariant(variantToDelete.value.id);
    variants.value = variants.value.filter((v) => v.id !== variantToDelete.value?.id);
    toast.show(`Đã xóa biến thể ${variantToDelete.value.sku}!`, "success");
    showDeleteConfirm.value = false;
  } catch (err) {
    toast.show(toAppError(err).message, "error");
  } finally {
    deleteLoading.value = false;
    variantToDelete.value = null;
  }
}

function getProductName(prodId: number): string {
  const p = products.value.find((item) => item.id === prodId);
  return p ? p.name : `#${String(prodId)}`;
}

function getSizeLabel(sizeId: number | null): string {
  if (!sizeId) return "—";
  const s = sizes.value.find((item) => item.id === sizeId);
  return s ? `EU ${s.label}` : `#${String(sizeId)}`;
}

function getColor(colorId: number | null): AdminColor | null {
  if (!colorId) return null;
  return colors.value.find((item) => item.id === colorId) || null;
}

function formatPrice(amount: string | number): string {
  return new Intl.NumberFormat("vi-VN").format(Number(amount)) + " ₫";
}

onMounted(() => {
  void loadData();
});
</script>

<template>
  <AdminLayout>
    <div class="space-y-6">
      <!-- Header -->
      <div
        class="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4 border-b border-white/10 pb-6"
      >
        <div>
          <span class="text-xs font-bold uppercase tracking-widest text-emerald-400"
            >Quản lý Catalog</span
          >
          <h1 class="text-2xl sm:text-3xl font-black uppercase tracking-tight text-white mt-1">
            Biến Thể Sản Phẩm (SKU)
          </h1>
          <p class="text-xs sm:text-sm text-slate-400 mt-1">
            Quản lý từng biến thể SKU liên kết Sản phẩm + Kích cỡ + Màu sắc + Giá bán và Tồn kho.
          </p>
        </div>
        <div class="flex items-center gap-3">
          <BaseButton variant="secondary" size="sm" @click="loadData"> Làm mới </BaseButton>
          <BaseButton variant="primary" size="sm" class="gap-2" @click="openCreateModal">
            <svg class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path
                stroke-linecap="round"
                stroke-linejoin="round"
                stroke-width="2"
                d="M12 4v16m8-8H4"
              />
            </svg>
            Tạo Biến Thể SKU
          </BaseButton>
        </div>
      </div>

      <div
        class="flex flex-col gap-3 rounded-2xl border border-sky-400/20 bg-sky-400/[0.06] p-4 sm:flex-row sm:items-center sm:justify-between"
      >
        <div>
          <p class="text-xs font-black tracking-wider text-sky-300 uppercase">
            Mỗi SKU = Sản phẩm + Size + Màu
          </p>
          <p class="mt-1 text-xs leading-5 text-slate-400">
            Danh sách size tự lọc theo thương hiệu của sản phẩm đã chọn, tránh gán nhầm bảng size
            giữa các hãng.
          </p>
        </div>
        <AppLink
          to="/admin/catalog-settings"
          class="shrink-0 rounded-xl border border-sky-400/20 bg-sky-400/10 px-4 py-2 text-xs font-bold text-sky-200 no-underline hover:bg-sky-400/15"
          >Thiết lập size & màu</AppLink
        >
      </div>

      <!-- Filter Bar -->
      <div
        class="flex flex-wrap items-center gap-3 bg-[#12151e] p-3 rounded-2xl border border-white/10"
      >
        <span class="text-xs font-bold uppercase tracking-wider text-slate-400"
          >Lọc theo Sản phẩm:</span
        >
        <select
          v-model="selectedProductFilter"
          class="rounded-xl border border-white/15 bg-white/5 px-3 py-1.5 text-xs text-white focus:border-emerald-500 focus:outline-none max-w-xs"
        >
          <option value="" class="bg-[#12151e] text-white">
            Tất cả sản phẩm ({{ variants.length }} biến thể)
          </option>
          <option
            v-for="prod in products"
            :key="prod.id"
            :value="prod.id"
            class="bg-[#12151e] text-white"
          >
            {{ prod.name }}
          </option>
        </select>
        <AppLink
          to="/admin/inventory"
          class="ml-auto text-xs font-bold text-emerald-400 hover:text-emerald-300 underline"
        >
          → Chuyển sang Quản lý Kho Hàng
        </AppLink>
      </div>

      <AppAlert v-if="error" variant="error">{{ error }}</AppAlert>

      <!-- Table Section -->
      <div
        class="overflow-hidden rounded-2xl border border-white/10 bg-[#12151e]/85 backdrop-blur-xl"
      >
        <div
          v-if="loading"
          class="p-8 text-center text-slate-400 text-xs font-bold uppercase tracking-wider flex items-center justify-center gap-3"
        >
          <svg class="h-5 w-5 animate-spin text-emerald-400" viewBox="0 0 24 24" fill="none">
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
          Đang tải danh sách biến thể SKU…
        </div>

        <div v-else-if="filteredVariants.length === 0" class="p-12 text-center">
          <div
            class="inline-flex h-12 w-12 items-center justify-center rounded-2xl bg-white/5 text-slate-400 mb-3"
          >
            <svg class="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path
                stroke-linecap="round"
                stroke-linejoin="round"
                stroke-width="2"
                d="M20 7l-8-4-8 4m16 0l-8 4m8-4v10l-8 4m0-10L4 7m8 4v10M4 7v10l8 4"
              />
            </svg>
          </div>
          <p class="text-sm font-bold text-white">Chưa có biến thể SKU nào</p>
          <p class="text-xs text-slate-400 mt-1">
            Bấm "Tạo Biến Thể SKU" để liên kết size, màu và giá bán cho sản phẩm.
          </p>
        </div>

        <table v-else class="w-full text-left text-sm text-slate-300">
          <thead
            class="border-b border-white/10 bg-white/5 text-[11px] font-bold uppercase tracking-wider text-slate-400"
          >
            <tr>
              <th scope="col" class="py-3.5 pl-6 pr-3">SKU</th>
              <th scope="col" class="px-3 py-3.5">Sản phẩm</th>
              <th scope="col" class="px-3 py-3.5">Kích cỡ</th>
              <th scope="col" class="px-3 py-3.5">Màu sắc</th>
              <th scope="col" class="px-3 py-3.5">Giá bán</th>
              <th scope="col" class="px-3 py-3.5">Tồn kho</th>
              <th scope="col" class="px-3 py-3.5">Trạng thái</th>
              <th scope="col" class="py-3.5 pl-3 pr-6 text-right">Thao tác</th>
            </tr>
          </thead>
          <tbody class="divide-y divide-white/5">
            <tr
              v-for="variant in filteredVariants"
              :key="variant.id"
              class="hover:bg-white/[0.02] transition-colors"
            >
              <td class="whitespace-nowrap py-4 pl-6 pr-3">
                <span
                  class="inline-flex items-center px-2 py-0.5 rounded-lg bg-emerald-500/10 text-emerald-400 border border-emerald-500/20 font-mono font-black text-xs"
                >
                  {{ variant.sku }}
                </span>
              </td>
              <td class="px-3 py-4 text-xs font-bold text-white max-w-[200px] truncate">
                {{ getProductName(variant.product) }}
              </td>
              <td class="whitespace-nowrap px-3 py-4 text-xs font-mono text-slate-300">
                <span class="rounded bg-white/10 px-2 py-0.5 font-bold">
                  {{ getSizeLabel(variant.size) }}
                </span>
              </td>
              <td class="whitespace-nowrap px-3 py-4 text-xs">
                <div v-if="getColor(variant.color)" class="flex items-center gap-1.5">
                  <span
                    class="h-3.5 w-3.5 rounded-full border border-white/20"
                    :style="{ backgroundColor: getColor(variant.color)?.hex_code || '#ccc' }"
                  />
                  <span>{{ getColor(variant.color)?.name }}</span>
                </div>
                <span v-else class="text-slate-500">—</span>
              </td>
              <td class="whitespace-nowrap px-3 py-4 text-xs font-bold text-white">
                {{ formatPrice(variant.price) }}
              </td>
              <td class="whitespace-nowrap px-3 py-4 text-xs">
                <span
                  :class="[
                    'font-mono font-bold px-2 py-0.5 rounded',
                    variant.inventory_quantity > 0
                      ? 'bg-emerald-500/15 text-emerald-400'
                      : 'bg-rose-500/15 text-rose-400',
                  ]"
                >
                  {{ variant.inventory_quantity }} đôi
                </span>
              </td>
              <td class="whitespace-nowrap px-3 py-4 text-xs">
                <span
                  :class="[
                    'inline-flex items-center rounded-md px-2 py-0.5 text-[10px] font-bold uppercase tracking-wider',
                    variant.is_active
                      ? 'bg-emerald-500/15 text-emerald-400 border border-emerald-500/30'
                      : 'bg-rose-500/15 text-rose-400 border border-rose-500/30',
                  ]"
                >
                  {{ variant.is_active ? "Bán" : "Ngừng" }}
                </span>
              </td>
              <td class="whitespace-nowrap py-4 pl-3 pr-6 text-right text-xs">
                <div class="flex items-center justify-end gap-2">
                  <button
                    type="button"
                    class="rounded-lg bg-white/5 px-2.5 py-1.5 font-bold text-slate-300 hover:bg-white/10 hover:text-white transition-all cursor-pointer"
                    @click="openEditModal(variant)"
                  >
                    Sửa
                  </button>
                  <button
                    type="button"
                    class="rounded-lg bg-rose-500/10 px-2.5 py-1.5 font-bold text-rose-400 hover:bg-rose-500/20 transition-all cursor-pointer"
                    @click="confirmDelete(variant)"
                  >
                    Xóa
                  </button>
                </div>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <!-- Create / Edit Variant Modal -->
    <Teleport to="body">
      <div
        v-if="showModal"
        class="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/80 backdrop-blur-sm overflow-y-auto"
        role="dialog"
        aria-modal="true"
      >
        <div
          class="relative w-full max-w-lg rounded-3xl border border-white/10 bg-[#12151e] p-6 shadow-2xl my-8"
        >
          <div class="mb-5 flex items-center justify-between">
            <h2 class="text-lg font-black uppercase tracking-tight text-white">
              {{ isEditing ? "Cập Nhật Biến Thể SKU" : "Tạo Biến Thể SKU Mới" }}
            </h2>
            <button
              type="button"
              class="rounded-lg p-1 text-slate-400 hover:bg-white/10 hover:text-white transition-all cursor-pointer"
              @click="showModal = false"
            >
              <svg class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path
                  stroke-linecap="round"
                  stroke-linejoin="round"
                  stroke-width="2"
                  d="M6 18L18 6M6 6l12 12"
                />
              </svg>
            </button>
          </div>

          <AppAlert v-if="formError" variant="error" class="mb-4">{{ formError }}</AppAlert>

          <form class="space-y-4" @submit.prevent="handleFormSubmit">
            <!-- Product -->
            <div>
              <label class="block text-xs font-bold uppercase tracking-wider text-slate-300 mb-1.5">
                Sản phẩm <span class="text-rose-400">*</span>
              </label>
              <select
                v-model="formData.product"
                required
                :disabled="isEditing"
                class="w-full rounded-xl border border-white/15 bg-white/5 px-3 py-2.5 text-sm text-white focus:border-emerald-500 focus:outline-none focus:ring-1 focus:ring-emerald-500 disabled:opacity-50"
              >
                <option value="" disabled class="bg-[#12151e] text-slate-400">
                  -- Chọn sản phẩm --
                </option>
                <option
                  v-for="p in products"
                  :key="p.id"
                  :value="p.id"
                  class="bg-[#12151e] text-white"
                >
                  {{ p.name }}
                </option>
              </select>
            </div>

            <!-- Size & Color Grid -->
            <div class="grid grid-cols-1 sm:grid-cols-2 gap-4">
              <div>
                <label
                  class="block text-xs font-bold uppercase tracking-wider text-slate-300 mb-1.5"
                >
                  Kích cỡ (Size)
                </label>
                <select
                  v-model="formData.size"
                  class="w-full rounded-xl border border-white/15 bg-white/5 px-3 py-2.5 text-sm text-white focus:border-emerald-500 focus:outline-none focus:ring-1 focus:ring-emerald-500"
                >
                  <option value="" class="bg-[#12151e] text-slate-400">
                    -- Không chọn size --
                  </option>
                  <option
                    v-for="s in availableSizes"
                    :key="s.id"
                    :value="s.id"
                    class="bg-[#12151e] text-white"
                  >
                    EU {{ s.label }} ({{ s.brand_name }})
                  </option>
                </select>
              </div>

              <div>
                <label
                  class="block text-xs font-bold uppercase tracking-wider text-slate-300 mb-1.5"
                >
                  Màu sắc (Color)
                </label>
                <select
                  v-model="formData.color"
                  class="w-full rounded-xl border border-white/15 bg-white/5 px-3 py-2.5 text-sm text-white focus:border-emerald-500 focus:outline-none focus:ring-1 focus:ring-emerald-500"
                >
                  <option value="" class="bg-[#12151e] text-slate-400">-- Không chọn màu --</option>
                  <option
                    v-for="c in colors"
                    :key="c.id"
                    :value="c.id"
                    class="bg-[#12151e] text-white"
                  >
                    {{ c.name }}
                  </option>
                </select>
              </div>
            </div>

            <!-- SKU -->
            <FormField
              v-slot="field"
              label="Quy cách phụ kiện"
              name="option-label"
              help="Ví dụ: Freesize 39–44, Chai 250 ml. Có thể bỏ trống với giày."
            >
              <BaseInput
                v-model="formData.option_label"
                :id="field.id"
                name="option_label"
                placeholder="Freesize hoặc Chai 250 ml"
              />
            </FormField>

            <!-- SKU -->
            <FormField
              v-slot="field"
              label="Mã SKU định danh"
              name="variant-sku"
              required
              help="Mã tồn kho duy nhất"
            >
              <BaseInput
                :id="field.id"
                name="variant_sku"
                v-model="formData.sku"
                placeholder="NIKE-AM360-42-BLK"
                required
              />
            </FormField>

            <!-- Price & Threshold Grid -->
            <div class="grid grid-cols-1 sm:grid-cols-2 gap-4">
              <div>
                <label
                  class="block text-xs font-bold uppercase tracking-wider text-slate-300 mb-1.5"
                >
                  Giá bán (VND) <span class="text-rose-400">*</span>
                </label>
                <input
                  type="number"
                  v-model="formData.price"
                  required
                  placeholder="1500000"
                  class="w-full rounded-xl border border-white/15 bg-white/5 px-3 py-2 text-sm text-white focus:border-emerald-500 focus:outline-none font-mono"
                />
              </div>

              <div>
                <label
                  class="block text-xs font-bold uppercase tracking-wider text-slate-300 mb-1.5"
                >
                  Ngưỡng báo sắp hết
                </label>
                <input
                  type="number"
                  v-model.number="formData.low_stock_threshold"
                  placeholder="5"
                  class="w-full rounded-xl border border-white/15 bg-white/5 px-3 py-2 text-sm text-white focus:border-emerald-500 focus:outline-none font-mono"
                />
              </div>
            </div>

            <!-- Is Active -->
            <div class="flex items-center gap-2 pt-2">
              <input
                id="variant-active"
                v-model="formData.is_active"
                type="checkbox"
                class="h-4 w-4 rounded border-white/20 bg-white/5 text-emerald-500 focus:ring-emerald-500"
              />
              <label
                for="variant-active"
                class="text-xs font-bold uppercase tracking-wider text-slate-300 cursor-pointer"
              >
                Kích hoạt bán biến thể này
              </label>
            </div>

            <!-- Action buttons -->
            <div class="mt-6 flex items-center justify-end gap-3 pt-4 border-t border-white/10">
              <BaseButton type="button" variant="secondary" size="sm" @click="showModal = false">
                Hủy bỏ
              </BaseButton>
              <BaseButton type="submit" variant="primary" size="sm" :loading="submitting">
                {{ isEditing ? "Lưu Thay Đổi" : "Tạo Biến Thể" }}
              </BaseButton>
            </div>
          </form>
        </div>
      </div>
    </Teleport>

    <!-- Delete Confirmation Modal -->
    <AppPopup
      v-model="showDeleteConfirm"
      mode="confirm"
      variant="error"
      title="Xác nhận xóa biến thể SKU"
      :message="`Hành động này sẽ xóa biến thể SKU '${variantToDelete?.sku}' khỏi hệ thống.`"
      action-text="Xóa vĩnh viễn"
      cancel-text="Hủy bỏ"
      :loading="deleteLoading"
      @confirm="handleDelete"
      @cancel="showDeleteConfirm = false"
    />
  </AdminLayout>
</template>
