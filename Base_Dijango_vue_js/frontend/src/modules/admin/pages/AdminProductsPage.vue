<script setup lang="ts">
import { onMounted, reactive, ref } from "vue";

import BaseButton from "@/components/base/BaseButton.vue";
import BaseInput from "@/components/base/BaseInput.vue";
import AppAlert from "@/components/feedback/AppAlert.vue";
import AppPopup from "@/components/feedback/AppPopup.vue";
import FormField from "@/components/form/FormField.vue";
import AppLink from "@/components/navigation/AppLink.vue";
import AdminLayout from "@/layouts/AdminLayout.vue";
import { useToastStore } from "@/app/stores/toast";
import { toAppError } from "@/lib/http/errors";
import { fetchBrands, fetchCategories } from "@/modules/catalog/api";
import type { Brand, Category } from "@/modules/catalog/types";
import { toSlug } from "../slug";
import {
  createProduct,
  deleteProduct,
  fetchAdminProducts,
  fetchAdminProductImages,
  uploadAdminProductImage,
  updateAdminProductImage,
  deleteAdminProductImage,
  updateProduct,
  updateProductStatus,
  type AdminProduct,
  type AdminProductImage,
  type CreateProductInput,
} from "../api";

const toast = useToastStore();
const products = ref<AdminProduct[]>([]);
const categories = ref<Category[]>([]);
const brands = ref<Brand[]>([]);
const loading = ref(true);
const error = ref("");
const updatingId = ref<number | null>(null);

// Modal Create / Edit state
const showFormModal = ref(false);
const isEditing = ref(false);
const editingProductId = ref<number | null>(null);
const formSubmitting = ref(false);
const formError = ref("");

const formData = reactive<{
  name: string;
  slug: string;
  category: number | "";
  brand: number | "";
  description: string;
  product_type: "footwear" | "accessory" | "care";
  status: "draft" | "published";
}>({
  name: "",
  slug: "",
  category: "",
  brand: "",
  description: "",
  product_type: "footwear",
  status: "published",
});

// Delete Confirmation Modal state
const showDeleteConfirm = ref(false);
const productToDelete = ref<AdminProduct | null>(null);
const deleteLoading = ref(false);

// Image Management Modal state
const showImageModal = ref(false);
const selectedProductForImages = ref<AdminProduct | null>(null);
const productImages = ref<AdminProductImage[]>([]);
const loadingImages = ref(false);
const uploadingImage = ref(false);
const uploadError = ref("");
const newImageFile = ref<File | null>(null);
const newImageAlt = ref("");
const newImageIsPrimary = ref(false);

async function openImageModal(product: AdminProduct) {
  selectedProductForImages.value = product;
  showImageModal.value = true;
  uploadError.value = "";
  newImageFile.value = null;
  newImageAlt.value = "";
  newImageIsPrimary.value = false;
  await loadProductImages(product.id);
}

async function loadProductImages(productId: number) {
  loadingImages.value = true;
  try {
    productImages.value = await fetchAdminProductImages(productId);
  } catch (err) {
    toast.show(toAppError(err).message, "error");
  } finally {
    loadingImages.value = false;
  }
}

function handleFileChange(event: Event) {
  const input = event.target as HTMLInputElement;
  if (input.files && input.files[0]) {
    newImageFile.value = input.files[0];
  }
}

async function handleUploadImage() {
  if (!selectedProductForImages.value || !newImageFile.value) {
    uploadError.value = "Vui lòng chọn tệp ảnh để tải lên.";
    return;
  }
  uploadingImage.value = true;
  uploadError.value = "";
  try {
    const fd = new FormData();
    fd.append("product", String(selectedProductForImages.value.id));
    fd.append("image", newImageFile.value);
    if (newImageAlt.value.trim()) {
      fd.append("alt_text", newImageAlt.value.trim());
    }
    fd.append("is_primary", String(newImageIsPrimary.value));
    fd.append("sort_order", String(productImages.value.length + 1));

    const created = await uploadAdminProductImage(fd);
    if (created.is_primary) {
      productImages.value.forEach((img) => (img.is_primary = false));
    }
    productImages.value.push(created);
    newImageFile.value = null;
    newImageAlt.value = "";
    newImageIsPrimary.value = false;
    toast.show("Tải lên ảnh thành công!", "success");
  } catch (err) {
    uploadError.value = toAppError(err).message;
  } finally {
    uploadingImage.value = false;
  }
}

async function handleSetPrimaryImage(img: AdminProductImage) {
  try {
    const updated = await updateAdminProductImage(img.id, { is_primary: true });
    productImages.value.forEach((i) => (i.is_primary = i.id === updated.id));
    toast.show("Đã đặt làm ảnh đại diện chính!", "success");
  } catch (err) {
    toast.show(toAppError(err).message, "error");
  }
}

async function handleDeleteImage(imgId: number) {
  try {
    await deleteAdminProductImage(imgId);
    productImages.value = productImages.value.filter((i) => i.id !== imgId);
    toast.show("Đã xóa ảnh!", "success");
  } catch (err) {
    toast.show(toAppError(err).message, "error");
  }
}

async function loadData() {
  loading.value = true;
  error.value = "";
  try {
    const [productsRes, categoriesRes, brandsRes] = await Promise.all([
      fetchAdminProducts(),
      fetchCategories().catch(() => []),
      fetchBrands().catch(() => []),
    ]);
    products.value = productsRes;
    categories.value = categoriesRes;
    brands.value = brandsRes;
  } catch (err) {
    error.value = toAppError(err).message;
  } finally {
    loading.value = false;
  }
}

const reloadingCatalogOptions = ref(false);
async function reloadCatalogOptions() {
  reloadingCatalogOptions.value = true;
  try {
    const [categoriesRes, brandsRes] = await Promise.all([
      fetchCategories().catch(() => []),
      fetchBrands().catch(() => []),
    ]);
    categories.value = categoriesRes;
    brands.value = brandsRes;
    toast.show("Đã làm mới danh mục & thương hiệu!", "success");
  } catch {
    toast.show("Không thể tải lại danh mục & thương hiệu", "error");
  } finally {
    reloadingCatalogOptions.value = false;
  }
}

function handleNameChange(name: string) {
  formData.name = name;
  if (!isEditing.value) {
    formData.slug = toSlug(name);
  }
}

function openCreateModal() {
  isEditing.value = false;
  editingProductId.value = null;
  formError.value = "";
  formData.name = "";
  formData.slug = "";
  formData.category = categories.value[0]?.id ?? "";
  formData.brand = brands.value[0]?.id ?? "";
  formData.description = "";
  formData.product_type = "footwear";
  formData.status = "published";
  showFormModal.value = true;
}

function openEditModal(product: AdminProduct) {
  isEditing.value = true;
  editingProductId.value = product.id;
  formError.value = "";
  formData.name = product.name;
  formData.slug = product.slug;
  formData.category = product.category;
  formData.brand = product.brand;
  formData.description = product.description || "";
  formData.product_type = product.product_type;
  formData.status = product.status;
  showFormModal.value = true;
}

async function handleFormSubmit() {
  if (!formData.name.trim()) {
    formError.value = "Vui lòng nhập tên sản phẩm.";
    return;
  }
  if (!formData.slug.trim()) {
    formError.value = "Vui lòng nhập đường dẫn slug.";
    return;
  }
  if (!formData.category) {
    formError.value = "Vui lòng chọn danh mục.";
    return;
  }
  if (!formData.brand) {
    formError.value = "Vui lòng chọn thương hiệu.";
    return;
  }

  formSubmitting.value = true;
  formError.value = "";

  try {
    if (isEditing.value && editingProductId.value) {
      const updated = await updateProduct(editingProductId.value, {
        name: formData.name.trim(),
        slug: formData.slug.trim(),
        category: formData.category,
        brand: formData.brand,
        description: formData.description.trim(),
        product_type: formData.product_type,
        status: formData.status,
      });

      const idx = products.value.findIndex((p) => p.id === updated.id);
      if (idx !== -1) {
        products.value[idx] = updated;
      }
      toast.show("Cập nhật thông tin sản phẩm thành công!", "success");
    } else {
      const payload: CreateProductInput = {
        name: formData.name.trim(),
        slug: formData.slug.trim(),
        category: formData.category,
        brand: formData.brand,
        description: formData.description.trim(),
        product_type: formData.product_type,
        status: formData.status,
      };
      const created = await createProduct(payload);
      products.value.unshift(created);
      toast.show("Tạo mới sản phẩm thành công!", "success");
    }
    showFormModal.value = false;
  } catch (err) {
    formError.value = toAppError(err).message;
    toast.show(formError.value, "error");
  } finally {
    formSubmitting.value = false;
  }
}

function promptDelete(product: AdminProduct) {
  productToDelete.value = product;
  showDeleteConfirm.value = true;
}

async function confirmDelete() {
  if (!productToDelete.value) return;
  deleteLoading.value = true;
  try {
    await deleteProduct(productToDelete.value.id);
    products.value = products.value.filter((p) => p.id !== productToDelete.value?.id);
    toast.show(`Đã xóa sản phẩm "${productToDelete.value.name}" thành công.`, "success");
    showDeleteConfirm.value = false;
    productToDelete.value = null;
  } catch (err) {
    toast.show(toAppError(err).message, "error");
  } finally {
    deleteLoading.value = false;
  }
}

async function togglePublish(product: AdminProduct) {
  const nextStatus = product.status === "published" ? "draft" : "published";
  updatingId.value = product.id;
  try {
    const updated = await updateProductStatus(product.id, nextStatus);
    product.status = updated.status;
    product.published_at = updated.published_at;
    toast.show(
      `Đã chuyển trạng thái sang ${nextStatus === "published" ? "Đã xuất bản" : "Bản nháp"}.`,
      "success",
    );
  } catch (err) {
    toast.show(toAppError(err).message, "error");
  } finally {
    updatingId.value = null;
  }
}

function formatDate(dateStr: string | null) {
  if (!dateStr) return "Chưa xuất bản";
  return new Date(dateStr).toLocaleDateString("vi-VN", {
    year: "numeric",
    month: "2-digit",
    day: "2-digit",
    hour: "2-digit",
    minute: "2-digit",
  });
}

function getCategoryName(categoryId: number) {
  const cat = categories.value.find((c) => c.id === categoryId);
  return cat ? cat.name : `#${String(categoryId)}`;
}

function getBrandName(brandId: number) {
  const br = brands.value.find((b) => b.id === brandId);
  return br ? br.name : `#${String(brandId)}`;
}

onMounted(loadData);
</script>

<template>
  <AdminLayout>
    <div class="space-y-6">
      <!-- Page Header -->
      <div class="flex flex-wrap items-center justify-between gap-4 border-b border-white/10 pb-5">
        <div>
          <p class="text-xs font-bold uppercase tracking-widest text-emerald-400">
            Quản Lý Catalog
          </p>
          <h1 class="text-2xl sm:text-3xl font-black uppercase tracking-tight text-white mt-1">
            Sản phẩm
          </h1>
          <p class="text-sm text-slate-400 mt-1">
            Quản lý nội dung chung, trạng thái xuất bản và hình ảnh. Giá, size, màu nằm ở biến thể
            SKU.
          </p>
        </div>
        <div class="flex items-center gap-3">
          <BaseButton
            size="sm"
            variant="secondary"
            class="rounded-xl border border-white/15"
            @click="loadData"
          >
            Làm mới
          </BaseButton>
          <BaseButton
            size="sm"
            class="rounded-xl bg-emerald-500 font-bold uppercase tracking-wider text-slate-950 hover:bg-emerald-400 shadow-[0_0_20px_rgba(16,185,129,0.3)] flex items-center gap-1.5"
            @click="openCreateModal"
          >
            <svg
              class="h-4 w-4"
              fill="none"
              viewBox="0 0 24 24"
              stroke="currentColor"
              stroke-width="2.5"
            >
              <path stroke-linecap="round" stroke-linejoin="round" d="M12 4.5v15m7.5-7.5h-15" />
            </svg>
            Thêm sản phẩm mới
          </BaseButton>
        </div>
      </div>

      <div class="grid gap-3 rounded-2xl border border-white/10 bg-[#12151e] p-4 sm:grid-cols-3">
        <AppLink
          to="/admin/catalog-settings"
          class="rounded-xl border border-white/10 bg-white/[0.025] p-3 text-xs text-slate-300 no-underline hover:border-emerald-500/30"
        >
          <strong class="block text-emerald-400">01 · Chuẩn bị thuộc tính</strong>
          <span class="mt-1 block leading-5 text-slate-500"
            >Danh mục và thương hiệu được tạo một lần trong Thiết lập catalog.</span
          >
        </AppLink>
        <div class="rounded-xl border border-emerald-500/30 bg-emerald-500/[0.07] p-3 text-xs">
          <strong class="block text-white">02 · Tạo sản phẩm</strong>
          <span class="mt-1 block leading-5 text-slate-400"
            >Tên, nội dung, hình ảnh và trạng thái bán.</span
          >
        </div>
        <AppLink
          to="/admin/variants"
          class="rounded-xl border border-white/10 bg-white/[0.025] p-3 text-xs text-slate-300 no-underline hover:border-emerald-500/30"
        >
          <strong class="block text-emerald-400">03 · Tạo SKU</strong>
          <span class="mt-1 block leading-5 text-slate-500"
            >Ghép sản phẩm với size, màu, giá và tồn kho.</span
          >
        </AppLink>
      </div>

      <AppAlert v-if="error" variant="error" title="Lỗi tải sản phẩm">{{ error }}</AppAlert>

      <!-- Loading State -->
      <div v-if="loading" class="p-12 text-center text-slate-400" role="status">
        <svg
          class="mx-auto h-8 w-8 animate-spin text-emerald-400 mb-3"
          viewBox="0 0 24 24"
          fill="none"
        >
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
        <span class="text-sm font-semibold">Đang tải danh sách sản phẩm từ backend…</span>
      </div>

      <!-- Empty State -->
      <div
        v-else-if="products.length === 0"
        class="rounded-3xl border border-dashed border-white/15 bg-white/5 p-12 text-center"
      >
        <div
          class="mx-auto mb-3 flex h-14 w-14 items-center justify-center rounded-2xl bg-white/5 text-slate-400"
        >
          <svg class="h-7 w-7" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path
              stroke-linecap="round"
              stroke-linejoin="round"
              stroke-width="1.5"
              d="M20 7l-8-4-8 4m16 0l-8 4m8-4v10l-8 4m0-10L4 7m8 4v10M4 7v10l8 4"
            />
          </svg>
        </div>
        <h3 class="text-lg font-bold text-white">Chưa có sản phẩm nào trong Catalog</h3>
        <p class="mt-1 text-sm text-slate-400 max-w-md mx-auto">
          Cơ sở dữ liệu backend hiện chưa có bản ghi Product nào. Hãy bấm "Thêm sản phẩm mới" để bắt
          đầu.
        </p>
        <div class="mt-5">
          <BaseButton
            size="sm"
            class="rounded-xl bg-emerald-500 font-bold uppercase tracking-wider text-slate-950 hover:bg-emerald-400 shadow-[0_0_20px_rgba(16,185,129,0.3)]"
            @click="openCreateModal"
          >
            + Thêm sản phẩm đầu tiên
          </BaseButton>
        </div>
      </div>

      <!-- Products Table -->
      <div
        v-else
        class="overflow-hidden rounded-3xl border border-white/10 bg-[#12151e]/85 backdrop-blur-xl shadow-2xl"
      >
        <div class="overflow-x-auto">
          <table class="w-full text-left text-sm text-slate-300">
            <thead
              class="border-b border-white/10 bg-white/5 text-xs font-black uppercase tracking-wider text-slate-400"
            >
              <tr>
                <th class="px-6 py-4">ID</th>
                <th class="px-6 py-4">Tên Sản Phẩm / Slug</th>
                <th class="px-6 py-4">Danh Mục & Thương Hiệu</th>
                <th class="px-6 py-4">Trạng Thái</th>
                <th class="px-6 py-4">Ngày Xuất Bản</th>
                <th class="px-6 py-4 text-right">Thao Tác</th>
              </tr>
            </thead>
            <tbody class="divide-y divide-white/5">
              <tr
                v-for="item in products"
                :key="item.id"
                class="transition-colors hover:bg-white/[0.02]"
              >
                <td class="px-6 py-4 font-mono text-xs font-bold text-slate-400">#{{ item.id }}</td>
                <td class="px-6 py-4">
                  <div class="font-bold text-white text-base">{{ item.name }}</div>
                  <div class="font-mono text-xs text-emerald-400/80 mt-0.5">{{ item.slug }}</div>
                  <p
                    v-if="item.description"
                    class="text-xs text-slate-400 mt-1 line-clamp-1 max-w-sm"
                  >
                    {{ item.description }}
                  </p>
                </td>
                <td class="px-6 py-4 text-xs">
                  <div class="font-semibold text-slate-200">
                    {{ getCategoryName(item.category) }}
                  </div>
                  <div class="text-slate-400 text-[11px] mt-0.5">
                    Hãng:
                    <span class="text-emerald-400 font-bold">{{ getBrandName(item.brand) }}</span>
                  </div>
                </td>
                <td class="px-6 py-4">
                  <div class="flex flex-wrap items-center gap-2.5">
                    <span
                      :class="[
                        'inline-flex items-center gap-1.5 rounded-full px-2.5 py-1 text-xs font-extrabold uppercase tracking-wider',
                        item.status === 'published'
                          ? 'border border-emerald-500/30 bg-emerald-500/15 text-emerald-400'
                          : 'border border-amber-500/30 bg-amber-500/15 text-amber-400',
                      ]"
                    >
                      <span
                        class="h-1.5 w-1.5 rounded-full"
                        :class="item.status === 'published' ? 'bg-emerald-400' : 'bg-amber-400'"
                      />
                      {{ item.status === "published" ? "Đã Xuất Bản" : "Bản Nháp" }}
                    </span>

                    <!-- Nút Đổi trạng thái để riêng biệt cạnh badge, tương phản rõ rệt cả nền sáng và tối -->
                    <button
                      type="button"
                      :disabled="updatingId === item.id"
                      :class="[
                        'inline-flex items-center gap-1 rounded-lg px-2.5 py-1 text-[11px] font-black uppercase tracking-wider transition-all duration-150 cursor-pointer border shadow-sm disabled:opacity-50',
                        item.status === 'published'
                          ? 'border-amber-500/50 bg-amber-500/15 text-amber-600 dark:text-amber-300 hover:bg-amber-500 hover:text-slate-950 dark:hover:bg-amber-400 dark:hover:text-slate-950 active:scale-95'
                          : 'border-emerald-500/50 bg-emerald-500/15 text-emerald-600 dark:text-emerald-300 hover:bg-emerald-500 hover:text-slate-950 dark:hover:bg-emerald-400 dark:hover:text-slate-950 active:scale-95',
                      ]"
                      :title="
                        item.status === 'published'
                          ? 'Chuyển về bản nháp'
                          : 'Xuất bản ra Storefront'
                      "
                      @click="togglePublish(item)"
                    >
                      <svg
                        v-if="updatingId === item.id"
                        class="h-3 w-3 animate-spin"
                        viewBox="0 0 24 24"
                        fill="none"
                      >
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
                      {{ item.status === "published" ? "Hạ nháp" : "Xuất bản" }}
                    </button>
                  </div>
                </td>
                <td class="px-6 py-4 text-xs font-medium text-slate-400">
                  {{ formatDate(item.published_at) }}
                </td>
                <td class="px-6 py-4 text-right">
                  <div class="flex items-center justify-end gap-2">
                    <!-- Quản lý ảnh -->
                    <button
                      type="button"
                      class="rounded-lg border border-purple-500/40 bg-purple-500/10 px-2.5 py-1 text-xs font-bold text-purple-400 hover:bg-purple-600 hover:text-white transition-all cursor-pointer shadow-sm active:scale-95"
                      title="Quản lý thư viện ảnh"
                      @click="openImageModal(item)"
                    >
                      Ảnh
                    </button>

                    <!-- Sửa -->
                    <button
                      type="button"
                      class="rounded-lg border border-white/10 bg-white/5 px-2.5 py-1 text-xs font-bold text-slate-300 hover:border-emerald-500/50 hover:bg-emerald-500 hover:text-slate-950 dark:hover:bg-emerald-400 dark:hover:text-slate-950 transition-all cursor-pointer shadow-sm active:scale-95"
                      title="Chỉnh sửa sản phẩm"
                      @click="openEditModal(item)"
                    >
                      Sửa
                    </button>

                    <!-- Xóa -->
                    <button
                      type="button"
                      class="rounded-lg border border-rose-500/30 bg-rose-500/10 px-2.5 py-1 text-xs font-bold text-rose-400 hover:bg-rose-600 hover:text-white transition-all cursor-pointer shadow-sm active:scale-95"
                      title="Xóa sản phẩm"
                      @click="promptDelete(item)"
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
    </div>

    <!-- Modal Thêm / Sửa Sản Phẩm -->
    <Teleport to="body">
      <Transition name="popup-fade">
        <div
          v-if="showFormModal"
          class="fixed inset-0 z-50 flex items-center justify-center p-4 sm:p-6"
          role="dialog"
          aria-modal="true"
        >
          <div
            class="fixed inset-0 bg-black/80 backdrop-blur-md transition-opacity"
            aria-hidden="true"
            @click="!formSubmitting && (showFormModal = false)"
          />

          <div
            class="relative z-10 w-full max-w-lg overflow-hidden rounded-3xl border border-white/15 bg-[#12151e] p-6 sm:p-8 text-white shadow-[0_25px_70px_rgba(0,0,0,0.95)] max-h-[90vh] overflow-y-auto"
          >
            <!-- Close button -->
            <button
              type="button"
              class="absolute top-5 right-5 flex h-8 w-8 items-center justify-center rounded-full text-slate-400 hover:bg-white/10 hover:text-white transition-colors cursor-pointer"
              :disabled="formSubmitting"
              @click="showFormModal = false"
            >
              <svg
                class="h-4 w-4"
                fill="none"
                viewBox="0 0 24 24"
                stroke="currentColor"
                stroke-width="2.5"
              >
                <path stroke-linecap="round" stroke-linejoin="round" d="M6 18L18 6M6 6l12 12" />
              </svg>
            </button>

            <!-- Header -->
            <div class="mb-6">
              <span
                class="inline-flex items-center gap-1.5 rounded-md bg-emerald-500/15 border border-emerald-500/30 px-2 py-0.5 text-[10px] font-black uppercase tracking-wider text-emerald-400 mb-2"
              >
                {{ isEditing ? "Chỉnh Sửa" : "Thêm Mới" }}
              </span>
              <h2 class="text-xl font-black uppercase tracking-tight text-white">
                {{ isEditing ? "Chỉnh Sửa Sản Phẩm" : "Tạo Sản Phẩm Mới" }}
              </h2>
              <p class="text-xs text-slate-400 mt-1">
                Điền thông tin sản phẩm catalog để hiển thị trên hệ thống và liên kết với biến thể.
              </p>
            </div>

            <AppAlert v-if="formError" variant="error" class="mb-4">
              {{ formError }}
            </AppAlert>

            <form class="space-y-4" @submit.prevent="handleFormSubmit">
              <!-- Name -->
              <FormField v-slot="field" label="Tên sản phẩm" name="prod-name" required>
                <BaseInput
                  :id="field.id"
                  name="product_name"
                  :model-value="formData.name"
                  placeholder="Ví dụ: Nike Air Max 360"
                  required
                  @update:model-value="handleNameChange"
                />
              </FormField>

              <!-- Slug -->
              <FormField
                v-slot="field"
                label="Đường dẫn tĩnh (Slug)"
                name="prod-slug"
                help="Định danh duy nhất trên URL (chỉ gồm chữ cái, số, dấu gạch ngang)"
                required
              >
                <BaseInput
                  :id="field.id"
                  name="product_slug"
                  v-model="formData.slug"
                  placeholder="nike-air-max-360"
                  required
                />
              </FormField>

              <!-- Category & Brand Alert if empty -->
              <div
                v-if="categories.length === 0 || brands.length === 0"
                class="rounded-xl border border-amber-500/30 bg-amber-500/10 p-3.5 text-xs text-amber-200 flex items-start gap-3"
              >
                <svg
                  class="h-5 w-5 text-amber-400 mt-0.5 flex-shrink-0"
                  fill="none"
                  viewBox="0 0 24 24"
                  stroke="currentColor"
                >
                  <path
                    stroke-linecap="round"
                    stroke-linejoin="round"
                    stroke-width="2"
                    d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z"
                  />
                </svg>
                <div class="flex-1 space-y-1">
                  <p class="font-bold text-amber-300">
                    Cần có ít nhất 1 Danh mục và 1 Thương hiệu trong cơ sở dữ liệu để tạo sản phẩm!
                  </p>
                  <p class="text-slate-300">
                    Hoàn tất dữ liệu nền tại trang Thiết lập catalog, sau đó quay lại và bấm "Làm
                    mới":
                  </p>
                  <div class="pt-1 flex flex-wrap items-center gap-3">
                    <AppLink
                      to="/admin/catalog-settings"
                      target="_blank"
                      class="inline-flex items-center gap-1 font-semibold text-emerald-400 underline hover:text-emerald-300"
                    >
                      Mở Thiết lập catalog
                    </AppLink>
                  </div>
                </div>
              </div>

              <!-- Category & Brand Grid -->
              <div class="space-y-1">
                <div class="flex items-center justify-between">
                  <span class="text-[11px] font-bold uppercase tracking-wider text-slate-400"
                    >Phân loại sản phẩm</span
                  >
                  <div class="flex items-center gap-3">
                    <AppLink
                      to="/admin/catalog-settings"
                      target="_blank"
                      class="text-[11px] font-semibold text-slate-400 no-underline hover:text-emerald-400"
                      >Thiết lập catalog</AppLink
                    >
                    <button
                      type="button"
                      @click="reloadCatalogOptions"
                      :disabled="reloadingCatalogOptions"
                      class="inline-flex items-center gap-1 text-[11px] font-semibold text-emerald-400 hover:text-emerald-300 transition-colors disabled:opacity-50 cursor-pointer"
                    >
                      <svg
                        :class="['h-3.5 w-3.5', reloadingCatalogOptions ? 'animate-spin' : '']"
                        fill="none"
                        viewBox="0 0 24 24"
                        stroke="currentColor"
                      >
                        <path
                          stroke-linecap="round"
                          stroke-linejoin="round"
                          stroke-width="2"
                          d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15"
                        />
                      </svg>
                      {{ reloadingCatalogOptions ? "Đang tải…" : "Làm mới" }}
                    </button>
                  </div>
                </div>

                <div class="grid grid-cols-1 sm:grid-cols-2 gap-4">
                  <div>
                    <label
                      class="block text-xs font-bold uppercase tracking-wider text-slate-300 mb-1.5"
                    >
                      Danh mục <span class="text-rose-400">*</span>
                    </label>
                    <select
                      v-model="formData.category"
                      required
                      class="w-full rounded-xl border border-white/15 bg-white/5 px-3 py-2.5 text-sm text-white focus:border-emerald-500 focus:outline-none focus:ring-1 focus:ring-emerald-500"
                    >
                      <option value="" disabled class="bg-[#12151e] text-slate-400">
                        -- Chọn danh mục --
                      </option>
                      <option
                        v-for="cat in categories"
                        :key="cat.id"
                        :value="cat.id"
                        class="bg-[#12151e] text-white"
                      >
                        {{ cat.name }}
                      </option>
                    </select>
                    <div class="mt-1 flex justify-end text-[11px]">
                      <span class="text-slate-500">({{ categories.length }} danh mục)</span>
                    </div>
                  </div>

                  <div>
                    <label
                      class="block text-xs font-bold uppercase tracking-wider text-slate-300 mb-1.5"
                    >
                      Thương hiệu <span class="text-rose-400">*</span>
                    </label>
                    <select
                      v-model="formData.brand"
                      required
                      class="w-full rounded-xl border border-white/15 bg-white/5 px-3 py-2.5 text-sm text-white focus:border-emerald-500 focus:outline-none focus:ring-1 focus:ring-emerald-500"
                    >
                      <option value="" disabled class="bg-[#12151e] text-slate-400">
                        -- Chọn thương hiệu --
                      </option>
                      <option
                        v-for="br in brands"
                        :key="br.id"
                        :value="br.id"
                        class="bg-[#12151e] text-white"
                      >
                        {{ br.name }}
                      </option>
                    </select>
                    <div class="mt-1 flex justify-end text-[11px]">
                      <span class="text-slate-500">({{ brands.length }} thương hiệu)</span>
                    </div>
                  </div>
                </div>
              </div>

              <!-- Status -->
              <div>
                <label
                  class="mb-1.5 block text-xs font-bold tracking-wider text-slate-300 uppercase"
                >
                  Loại sản phẩm
                </label>
                <select
                  v-model="formData.product_type"
                  class="w-full rounded-xl border border-white/15 bg-white/5 px-3 py-2.5 text-sm text-white focus:border-emerald-500 focus:outline-none focus:ring-1 focus:ring-emerald-500"
                >
                  <option value="footwear" class="bg-[#12151e]">Giày dép — bắt buộc size</option>
                  <option value="accessory" class="bg-[#12151e]">Phụ kiện — size tùy chọn</option>
                  <option value="care" class="bg-[#12151e]">Chăm sóc giày</option>
                </select>
              </div>

              <!-- Status -->
              <div>
                <label
                  class="block text-xs font-bold uppercase tracking-wider text-slate-300 mb-1.5"
                >
                  Trạng thái
                </label>
                <select
                  v-model="formData.status"
                  class="w-full rounded-xl border border-white/15 bg-white/5 px-3 py-2.5 text-sm text-white focus:border-emerald-500 focus:outline-none focus:ring-1 focus:ring-emerald-500"
                >
                  <option value="published" class="bg-[#12151e] text-emerald-400">
                    Xuất bản ngay (Published)
                  </option>
                  <option value="draft" class="bg-[#12151e] text-amber-400">
                    Lưu bản nháp (Draft)
                  </option>
                </select>
              </div>

              <!-- Description -->
              <div>
                <label
                  class="block text-xs font-bold uppercase tracking-wider text-slate-300 mb-1.5"
                >
                  Mô tả sản phẩm
                </label>
                <textarea
                  v-model="formData.description"
                  rows="3"
                  placeholder="Mô tả công nghệ đệm, chất liệu upper..."
                  class="w-full rounded-xl border border-white/15 bg-white/5 p-3 text-sm text-white placeholder-slate-500 focus:border-emerald-500 focus:outline-none focus:ring-1 focus:ring-emerald-500 transition-colors"
                />
              </div>

              <!-- Modal Actions -->
              <div class="flex items-center justify-end gap-3 pt-4 border-t border-white/10">
                <BaseButton
                  type="button"
                  variant="ghost"
                  class="rounded-xl border border-white/15 text-slate-300 hover:text-white text-xs font-bold uppercase"
                  :disabled="formSubmitting"
                  @click="showFormModal = false"
                >
                  Hủy bỏ
                </BaseButton>
                <BaseButton
                  type="submit"
                  class="rounded-xl bg-emerald-500 px-5 text-xs font-black uppercase tracking-wider text-slate-950 hover:bg-emerald-400 shadow-[0_0_20px_rgba(16,185,129,0.3)]"
                  :loading="formSubmitting"
                >
                  {{ isEditing ? "Lưu thay đổi" : "Tạo sản phẩm" }}
                </BaseButton>
              </div>
            </form>
          </div>
        </div>
      </Transition>
    </Teleport>

    <!-- AppPopup Confirm Xóa Sản Phẩm -->
    <AppPopup
      v-model="showDeleteConfirm"
      mode="confirm"
      variant="error"
      title="Xác nhận xóa sản phẩm"
      :message="`Bạn có chắc chắn muốn xóa sản phẩm '${productToDelete?.name}' (#${productToDelete?.id})? Hành động này sẽ chuyển trạng thái sản phẩm sang ngưng hoạt động.`"
      action-text="Xóa vĩnh viễn"
      cancel-text="Giữ lại"
      :loading="deleteLoading"
      @confirm="confirmDelete"
      @cancel="showDeleteConfirm = false"
    />

    <!-- Modal Quản Lý Ảnh Sản Phẩm -->
    <Teleport to="body">
      <div
        v-if="showImageModal"
        class="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/80 backdrop-blur-sm overflow-y-auto"
        role="dialog"
        aria-modal="true"
      >
        <div
          class="relative w-full max-w-2xl rounded-3xl border border-white/10 bg-[#12151e] p-6 shadow-2xl my-8"
        >
          <!-- Modal Header -->
          <div class="mb-5 flex items-center justify-between border-b border-white/10 pb-4">
            <div>
              <span class="text-[10px] font-black uppercase tracking-widest text-purple-400"
                >Thư Viện Ảnh</span
              >
              <h2 class="text-lg font-black uppercase tracking-tight text-white mt-0.5">
                {{ selectedProductForImages?.name }}
              </h2>
            </div>
            <button
              type="button"
              class="rounded-lg p-1 text-slate-400 hover:bg-white/10 hover:text-white transition-all cursor-pointer"
              @click="showImageModal = false"
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

          <!-- Upload Form -->
          <div class="rounded-2xl border border-white/10 bg-white/[0.02] p-4 mb-6">
            <h3 class="text-xs font-bold uppercase tracking-wider text-slate-300 mb-3">
              Tải Lên Ảnh Mới
            </h3>
            <AppAlert v-if="uploadError" variant="error" class="mb-3">{{ uploadError }}</AppAlert>

            <form class="space-y-3" @submit.prevent="handleUploadImage">
              <div class="grid grid-cols-1 sm:grid-cols-2 gap-3">
                <div>
                  <label class="block text-[11px] font-bold uppercase text-slate-400 mb-1"
                    >Chọn tệp ảnh (JPEG/PNG/WebP, &lt; 5MB)</label
                  >
                  <input
                    type="file"
                    accept="image/jpeg,image/png,image/webp"
                    required
                    class="w-full text-xs text-slate-300 file:mr-3 file:py-1.5 file:px-3 file:rounded-xl file:border-0 file:text-xs file:font-bold file:bg-emerald-500/20 file:text-emerald-400 hover:file:bg-emerald-500/30 cursor-pointer"
                    @change="handleFileChange"
                  />
                </div>
                <div>
                  <label class="block text-[11px] font-bold uppercase text-slate-400 mb-1"
                    >Mô tả ảnh (Alt text)</label
                  >
                  <input
                    type="text"
                    v-model="newImageAlt"
                    placeholder="Mặt trước giày, đế giày..."
                    class="w-full rounded-xl border border-white/15 bg-white/5 px-3 py-1.5 text-xs text-white focus:border-emerald-500 focus:outline-none"
                  />
                </div>
              </div>

              <div class="flex items-center justify-between pt-1">
                <label class="flex items-center gap-2 cursor-pointer text-xs text-slate-300">
                  <input
                    type="checkbox"
                    v-model="newImageIsPrimary"
                    class="h-4 w-4 rounded border-white/20 bg-white/5 text-emerald-500 focus:ring-emerald-500"
                  />
                  <span>Đặt làm ảnh đại diện chính (Primary Thumbnail)</span>
                </label>
                <BaseButton type="submit" variant="primary" size="sm" :loading="uploadingImage">
                  Tải Lên Ảnh
                </BaseButton>
              </div>
            </form>
          </div>

          <!-- Existing Images Gallery -->
          <div>
            <h3 class="text-xs font-bold uppercase tracking-wider text-slate-300 mb-3">
              Danh Sách Ảnh ({{ productImages.length }})
            </h3>

            <div
              v-if="loadingImages"
              class="py-8 text-center text-slate-400 text-xs flex items-center justify-center gap-2"
            >
              <svg class="h-4 w-4 animate-spin text-emerald-400" viewBox="0 0 24 24" fill="none">
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
              Đang tải danh sách ảnh…
            </div>

            <div
              v-else-if="productImages.length === 0"
              class="rounded-xl border border-white/5 p-8 text-center text-xs text-slate-400"
            >
              Sản phẩm này chưa có ảnh nào. Vui lòng tải lên ảnh ở khung phía trên.
            </div>

            <div v-else class="grid grid-cols-2 sm:grid-cols-3 gap-3">
              <div
                v-for="img in productImages"
                :key="img.id"
                class="group relative rounded-2xl border border-white/10 bg-black/40 overflow-hidden p-2 flex flex-col justify-between"
              >
                <div
                  class="aspect-square w-full rounded-xl overflow-hidden bg-[#0c0e17] flex items-center justify-center mb-2"
                >
                  <img
                    :src="img.image_url"
                    :alt="img.alt_text || selectedProductForImages?.name"
                    class="h-full w-full object-cover"
                  />
                </div>

                <div class="flex items-center justify-between gap-1 text-[10px]">
                  <span
                    v-if="img.is_primary"
                    class="inline-flex items-center px-1.5 py-0.5 rounded bg-emerald-500/20 text-emerald-400 border border-emerald-500/30 font-bold uppercase"
                  >
                    Ảnh chính
                  </span>
                  <button
                    v-else
                    type="button"
                    class="text-slate-400 hover:text-emerald-400 underline cursor-pointer"
                    @click="handleSetPrimaryImage(img)"
                  >
                    Đặt làm chính
                  </button>

                  <button
                    type="button"
                    class="text-rose-400 hover:text-rose-300 font-bold cursor-pointer"
                    title="Xóa ảnh này"
                    @click="handleDeleteImage(img.id)"
                  >
                    Xóa
                  </button>
                </div>
              </div>
            </div>
          </div>

          <div class="mt-6 flex justify-end border-t border-white/10 pt-4">
            <BaseButton variant="secondary" size="sm" @click="showImageModal = false">
              Đóng
            </BaseButton>
          </div>
        </div>
      </div>
    </Teleport>
  </AdminLayout>
</template>

<style scoped>
.popup-fade-enter-active,
.popup-fade-leave-active {
  transition: opacity 0.2s ease;
}

.popup-fade-enter-active > div:last-child,
.popup-fade-leave-active > div:last-child {
  transition:
    transform 0.2s cubic-bezier(0.16, 1, 0.3, 1),
    opacity 0.2s ease;
}

.popup-fade-enter-from,
.popup-fade-leave-to {
  opacity: 0;
}

.popup-fade-enter-from > div:last-child {
  transform: scale(0.95) translateY(10px);
  opacity: 0;
}

.popup-fade-leave-to > div:last-child {
  transform: scale(0.98) translateY(4px);
  opacity: 0;
}
</style>
