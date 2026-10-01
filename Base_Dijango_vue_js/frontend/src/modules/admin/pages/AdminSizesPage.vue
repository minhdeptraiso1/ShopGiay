<script setup lang="ts">
import { computed, onMounted, reactive, ref } from "vue";

import BaseButton from "@/components/base/BaseButton.vue";
import BaseInput from "@/components/base/BaseInput.vue";
import AppAlert from "@/components/feedback/AppAlert.vue";
import AppPopup from "@/components/feedback/AppPopup.vue";
import FormField from "@/components/form/FormField.vue";
import AdminLayout from "@/layouts/AdminLayout.vue";
import { useToastStore } from "@/app/stores/toast";
import { toAppError } from "@/lib/http/errors";
import {
  createAdminSize,
  deleteAdminSize,
  fetchAdminBrands,
  fetchAdminSizes,
  updateAdminSize,
  type AdminBrand,
  type AdminSize,
  type CreateSizeInput,
} from "../api";

const toast = useToastStore();
const sizes = ref<AdminSize[]>([]);
const brands = ref<AdminBrand[]>([]);
const loading = ref(true);
const error = ref("");
const selectedBrandFilter = ref<number | "">("");

// Modal Create / Edit state
const showModal = ref(false);
const isEditing = ref(false);
const editingSizeId = ref<number | null>(null);
const submitting = ref(false);
const formError = ref("");

const formData = reactive<{
  brand: number | "";
  label: string;
  sort_order: number;
  is_active: boolean;
}>({
  brand: "",
  label: "",
  sort_order: 1,
  is_active: true,
});

// Delete Confirmation
const showDeleteConfirm = ref(false);
const sizeToDelete = ref<AdminSize | null>(null);
const deleteLoading = ref(false);

const filteredSizes = computed(() => {
  if (!selectedBrandFilter.value) return sizes.value;
  return sizes.value.filter((s) => s.brand === Number(selectedBrandFilter.value));
});

async function loadData() {
  loading.value = true;
  error.value = "";
  try {
    const [sizesRes, brandsRes] = await Promise.all([fetchAdminSizes(), fetchAdminBrands()]);
    sizes.value = sizesRes;
    brands.value = brandsRes;
  } catch (err) {
    error.value = toAppError(err).message;
  } finally {
    loading.value = false;
  }
}

function openCreateModal() {
  isEditing.value = false;
  editingSizeId.value = null;
  formError.value = "";
  formData.brand = brands.value.length > 0 ? (brands.value[0]?.id ?? "") : "";
  formData.label = "";
  formData.sort_order = sizes.value.length + 1;
  formData.is_active = true;
  showModal.value = true;
}

function openEditModal(size: AdminSize) {
  isEditing.value = true;
  editingSizeId.value = size.id;
  formError.value = "";
  formData.brand = size.brand;
  formData.label = size.label;
  formData.sort_order = size.sort_order;
  formData.is_active = size.is_active;
  showModal.value = true;
}

async function handleFormSubmit() {
  if (!formData.brand) {
    formError.value = "Vui lòng chọn thương hiệu.";
    return;
  }
  if (!formData.label.trim()) {
    formError.value = "Vui lòng nhập ít nhất một kích cỡ.";
    return;
  }
  const brandId = formData.brand;

  submitting.value = true;
  formError.value = "";

  try {
    if (isEditing.value && editingSizeId.value) {
      const updated = await updateAdminSize(editingSizeId.value, {
        brand: brandId,
        label: formData.label.trim(),
        sort_order: formData.sort_order,
        is_active: formData.is_active,
      });
      const idx = sizes.value.findIndex((s) => s.id === updated.id);
      if (idx !== -1) sizes.value[idx] = updated;
      toast.show("Cập nhật kích cỡ thành công!", "success");
    } else {
      const labels = [
        ...new Set(
          formData.label
            .split(/[\s,;]+/)
            .map((label) => label.trim())
            .filter(Boolean),
        ),
      ];
      const existingLabels = new Set(
        sizes.value
          .filter((size) => size.brand === brandId)
          .map((size) => size.label.toLocaleLowerCase()),
      );
      const newLabels = labels.filter((label) => !existingLabels.has(label.toLocaleLowerCase()));
      if (newLabels.length === 0) {
        formError.value = "Các kích cỡ này đã tồn tại cho thương hiệu đã chọn.";
        return;
      }
      const created = await Promise.all(
        newLabels.map((label, index) => {
          const payload: CreateSizeInput = {
            brand: brandId,
            label,
            sort_order: formData.sort_order + index,
            is_active: formData.is_active,
          };
          return createAdminSize(payload);
        }),
      );
      sizes.value.unshift(...created);
      toast.show(`Đã tạo ${String(created.length)} kích cỡ cho thương hiệu.`, "success");
    }
    showModal.value = false;
  } catch (err) {
    formError.value = toAppError(err).message;
  } finally {
    submitting.value = false;
  }
}

function confirmDelete(size: AdminSize) {
  sizeToDelete.value = size;
  showDeleteConfirm.value = true;
}

async function handleDelete() {
  if (!sizeToDelete.value) return;
  deleteLoading.value = true;
  try {
    await deleteAdminSize(sizeToDelete.value.id);
    sizes.value = sizes.value.filter((s) => s.id !== sizeToDelete.value?.id);
    toast.show(`Đã xóa kích cỡ ${sizeToDelete.value.label}!`, "success");
    showDeleteConfirm.value = false;
  } catch (err) {
    toast.show(toAppError(err).message, "error");
  } finally {
    deleteLoading.value = false;
    sizeToDelete.value = null;
  }
}

function getBrandName(brandId: number): string {
  const b = brands.value.find((item) => item.id === brandId);
  return b ? b.name : `#${String(brandId)}`;
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
            Kích Cỡ Giày (Sizes)
          </h1>
          <p class="text-xs sm:text-sm text-slate-400 mt-1">
            Quản lý các size giày phân loại theo thương hiệu (38, 39, 40, 41, 42, 42.5, 43, 44...).
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
            Thêm Dải Kích Cỡ
          </BaseButton>
        </div>
      </div>

      <!-- Filter Bar -->
      <div class="flex items-center gap-3 bg-[#12151e] p-3 rounded-2xl border border-white/10">
        <span class="text-xs font-bold uppercase tracking-wider text-slate-400"
          >Lọc theo Thương hiệu:</span
        >
        <select
          v-model="selectedBrandFilter"
          class="rounded-xl border border-white/15 bg-white/5 px-3 py-1.5 text-xs text-white focus:border-emerald-500 focus:outline-none"
        >
          <option value="" class="bg-[#12151e] text-white">
            Tất cả thương hiệu ({{ sizes.length }})
          </option>
          <option
            v-for="brand in brands"
            :key="brand.id"
            :value="brand.id"
            class="bg-[#12151e] text-white"
          >
            {{ brand.name }}
          </option>
        </select>
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
          Đang tải danh sách kích cỡ…
        </div>

        <div v-else-if="filteredSizes.length === 0" class="p-12 text-center">
          <div
            class="inline-flex h-12 w-12 items-center justify-center rounded-2xl bg-white/5 text-slate-400 mb-3"
          >
            <svg class="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path
                stroke-linecap="round"
                stroke-linejoin="round"
                stroke-width="2"
                d="M19 11H5m14 0a2 2 0 012 2v6a2 2 0 01-2 2H5a2 2 0 01-2-2v-6a2 2 0 012-2m14 0V9a2 2 0 00-2-2M5 11V9a2 2 0 012-2m0 0V5a2 2 0 012-2h6a2 2 0 012 2v2M7 7h10"
              />
            </svg>
          </div>
          <p class="text-sm font-bold text-white">Chưa có kích cỡ nào phù hợp</p>
          <p class="text-xs text-slate-400 mt-1">
            Bấm "Thêm Kích Cỡ Mới" để tạo size cho sản phẩm.
          </p>
        </div>

        <table v-else class="w-full text-left text-sm text-slate-300">
          <thead
            class="border-b border-white/10 bg-white/5 text-[11px] font-bold uppercase tracking-wider text-slate-400"
          >
            <tr>
              <th scope="col" class="py-3.5 pl-6 pr-3">ID</th>
              <th scope="col" class="px-3 py-3.5">Kích cỡ (Size)</th>
              <th scope="col" class="px-3 py-3.5">Thương hiệu</th>
              <th scope="col" class="px-3 py-3.5">Thứ tự</th>
              <th scope="col" class="px-3 py-3.5">Trạng thái</th>
              <th scope="col" class="py-3.5 pl-3 pr-6 text-right">Thao tác</th>
            </tr>
          </thead>
          <tbody class="divide-y divide-white/5">
            <tr
              v-for="size in filteredSizes"
              :key="size.id"
              class="hover:bg-white/[0.02] transition-colors"
            >
              <td class="whitespace-nowrap py-4 pl-6 pr-3 text-xs font-bold text-slate-400">
                #{{ size.id }}
              </td>
              <td class="whitespace-nowrap px-3 py-4">
                <span
                  class="inline-flex items-center px-2.5 py-1 rounded-lg bg-white/10 text-white font-mono font-black text-sm"
                >
                  EU {{ size.label }}
                </span>
              </td>
              <td class="whitespace-nowrap px-3 py-4 text-xs font-semibold text-emerald-400">
                {{ size.brand_name || getBrandName(size.brand) }}
              </td>
              <td class="whitespace-nowrap px-3 py-4 text-xs text-slate-400 font-mono">
                {{ size.sort_order }}
              </td>
              <td class="whitespace-nowrap px-3 py-4 text-xs">
                <span
                  :class="[
                    'inline-flex items-center rounded-md px-2 py-0.5 text-[10px] font-bold uppercase tracking-wider',
                    size.is_active
                      ? 'bg-emerald-500/15 text-emerald-400 border border-emerald-500/30'
                      : 'bg-rose-500/15 text-rose-400 border border-rose-500/30',
                  ]"
                >
                  {{ size.is_active ? "Hoạt động" : "Tạm tắt" }}
                </span>
              </td>
              <td class="whitespace-nowrap py-4 pl-3 pr-6 text-right text-xs">
                <div class="flex items-center justify-end gap-2">
                  <button
                    type="button"
                    class="rounded-lg bg-white/5 px-2.5 py-1.5 font-bold text-slate-300 hover:bg-white/10 hover:text-white transition-all cursor-pointer"
                    @click="openEditModal(size)"
                  >
                    Sửa
                  </button>
                  <button
                    type="button"
                    class="rounded-lg bg-rose-500/10 px-2.5 py-1.5 font-bold text-rose-400 hover:bg-rose-500/20 transition-all cursor-pointer"
                    @click="confirmDelete(size)"
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

    <!-- Create / Edit Size Modal -->
    <Teleport to="body">
      <div
        v-if="showModal"
        class="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/80 backdrop-blur-sm"
        role="dialog"
        aria-modal="true"
      >
        <div
          class="relative w-full max-w-md rounded-3xl border border-white/10 bg-[#12151e] p-6 shadow-2xl"
        >
          <div class="mb-5 flex items-center justify-between">
            <h2 class="text-lg font-black uppercase tracking-tight text-white">
              {{ isEditing ? "Cập Nhật Kích Cỡ" : "Thêm Dải Kích Cỡ" }}
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
            <!-- Brand -->
            <div>
              <label class="block text-xs font-bold uppercase tracking-wider text-slate-300 mb-1.5">
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
                  v-for="b in brands"
                  :key="b.id"
                  :value="b.id"
                  class="bg-[#12151e] text-white"
                >
                  {{ b.name }}
                </option>
              </select>
            </div>

            <!-- Label -->
            <FormField
              v-slot="field"
              :label="isEditing ? 'Kích cỡ' : 'Danh sách kích cỡ'"
              name="size-label"
              required
              :help="
                isEditing
                  ? 'Chỉnh sửa một kích cỡ.'
                  : 'Nhập nhiều size, cách nhau bằng dấu phẩy hoặc khoảng trắng. Ví dụ: 38, 39, 40, 41, 42.5'
              "
            >
              <BaseInput
                :id="field.id"
                name="size_label"
                v-model="formData.label"
                :placeholder="isEditing ? '42' : '38, 39, 40, 41, 42, 43'"
                required
              />
            </FormField>

            <!-- Sort order -->
            <div>
              <label class="block text-xs font-bold uppercase tracking-wider text-slate-300 mb-1.5">
                Thứ tự hiển thị
              </label>
              <input
                type="number"
                v-model.number="formData.sort_order"
                class="w-full rounded-xl border border-white/15 bg-white/5 px-3 py-2 text-sm text-white focus:border-emerald-500 focus:outline-none font-mono"
              />
              <p class="text-[11px] text-slate-400 mt-1">Số nhỏ hơn sẽ hiển thị trước</p>
            </div>

            <!-- Is Active -->
            <div class="flex items-center gap-2 pt-2">
              <input
                id="size-active"
                v-model="formData.is_active"
                type="checkbox"
                class="h-4 w-4 rounded border-white/20 bg-white/5 text-emerald-500 focus:ring-emerald-500"
              />
              <label
                for="size-active"
                class="text-xs font-bold uppercase tracking-wider text-slate-300 cursor-pointer"
              >
                Kích cỡ đang hoạt động
              </label>
            </div>

            <!-- Action buttons -->
            <div class="mt-6 flex items-center justify-end gap-3 pt-4 border-t border-white/10">
              <BaseButton type="button" variant="secondary" size="sm" @click="showModal = false">
                Hủy bỏ
              </BaseButton>
              <BaseButton type="submit" variant="primary" size="sm" :loading="submitting">
                {{ isEditing ? "Lưu Thay Đổi" : "Tạo Dải Kích Cỡ" }}
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
      title="Xác nhận xóa kích cỡ"
      :message="`Hành động này sẽ xóa kích cỡ EU ${sizeToDelete?.label} khỏi hệ thống. Các biến thể đang dùng kích cỡ này có thể bị ảnh hưởng.`"
      action-text="Xóa vĩnh viễn"
      cancel-text="Hủy bỏ"
      :loading="deleteLoading"
      @confirm="handleDelete"
      @cancel="showDeleteConfirm = false"
    />
  </AdminLayout>
</template>
