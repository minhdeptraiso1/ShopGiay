<script setup lang="ts">
import { onMounted, reactive, ref } from "vue";

import BaseButton from "@/components/base/BaseButton.vue";
import BaseInput from "@/components/base/BaseInput.vue";
import AppAlert from "@/components/feedback/AppAlert.vue";
import AppPopup from "@/components/feedback/AppPopup.vue";
import FormField from "@/components/form/FormField.vue";
import AdminLayout from "@/layouts/AdminLayout.vue";
import { useToastStore } from "@/app/stores/toast";
import { toAppError } from "@/lib/http/errors";
import { toSlug } from "../slug";
import {
  createAdminBrand,
  deleteAdminBrand,
  fetchAdminBrands,
  updateAdminBrand,
  type AdminBrand,
  type CreateBrandInput,
} from "../api";

const toast = useToastStore();
const brands = ref<AdminBrand[]>([]);
const loading = ref(true);
const error = ref("");

// Modal Create / Edit state
const showModal = ref(false);
const isEditing = ref(false);
const editingBrandId = ref<number | null>(null);
const submitting = ref(false);
const formError = ref("");

const formData = reactive<{
  name: string;
  slug: string;
  description: string;
  is_active: boolean;
}>({
  name: "",
  slug: "",
  description: "",
  is_active: true,
});

// Delete Confirmation
const showDeleteConfirm = ref(false);
const brandToDelete = ref<AdminBrand | null>(null);
const deleteLoading = ref(false);

async function loadBrands() {
  loading.value = true;
  error.value = "";
  try {
    brands.value = await fetchAdminBrands();
  } catch (err) {
    error.value = toAppError(err).message;
  } finally {
    loading.value = false;
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
  editingBrandId.value = null;
  formError.value = "";
  formData.name = "";
  formData.slug = "";
  formData.description = "";
  formData.is_active = true;
  showModal.value = true;
}

function openEditModal(brand: AdminBrand) {
  isEditing.value = true;
  editingBrandId.value = brand.id;
  formError.value = "";
  formData.name = brand.name;
  formData.slug = brand.slug;
  formData.description = brand.description || "";
  formData.is_active = brand.is_active;
  showModal.value = true;
}

async function handleFormSubmit() {
  if (!formData.name.trim()) {
    formError.value = "Vui lòng nhập tên thương hiệu.";
    return;
  }
  if (!formData.slug.trim()) {
    formError.value = "Vui lòng nhập slug thương hiệu.";
    return;
  }

  submitting.value = true;
  formError.value = "";

  try {
    if (isEditing.value && editingBrandId.value) {
      const updated = await updateAdminBrand(editingBrandId.value, {
        name: formData.name.trim(),
        slug: formData.slug.trim(),
        description: formData.description.trim(),
        is_active: formData.is_active,
      });

      const idx = brands.value.findIndex((b) => b.id === updated.id);
      if (idx !== -1) {
        brands.value[idx] = updated;
      }
      toast.show("Cập nhật thương hiệu thành công!", "success");
    } else {
      const payload: CreateBrandInput = {
        name: formData.name.trim(),
        slug: formData.slug.trim(),
        description: formData.description.trim(),
        is_active: formData.is_active,
      };
      const created = await createAdminBrand(payload);
      brands.value.push(created);
      toast.show("Thêm thương hiệu mới thành công!", "success");
    }
    showModal.value = false;
  } catch (err) {
    formError.value = toAppError(err).message;
    toast.show(formError.value, "error");
  } finally {
    submitting.value = false;
  }
}

function promptDelete(brand: AdminBrand) {
  brandToDelete.value = brand;
  showDeleteConfirm.value = true;
}

async function confirmDelete() {
  if (!brandToDelete.value) return;
  deleteLoading.value = true;
  try {
    await deleteAdminBrand(brandToDelete.value.id);
    brands.value = brands.value.filter((b) => b.id !== brandToDelete.value?.id);
    toast.show(`Đã xóa thương hiệu "${brandToDelete.value.name}" thành công.`, "success");
    showDeleteConfirm.value = false;
    brandToDelete.value = null;
  } catch (err) {
    toast.show(toAppError(err).message, "error");
  } finally {
    deleteLoading.value = false;
  }
}

onMounted(loadBrands);
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
            Thương Hiệu Giày
          </h1>
          <p class="text-sm text-slate-400 mt-1">
            Quản lý các thương hiệu sản phẩm giày (Nike, Adidas, Puma, Jordan, Converse...).
          </p>
        </div>
        <div class="flex items-center gap-3">
          <BaseButton
            size="sm"
            variant="ghost"
            class="rounded-xl border border-white/15 text-slate-300 hover:text-white"
            @click="loadBrands"
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
            Thêm thương hiệu mới
          </BaseButton>
        </div>
      </div>

      <AppAlert v-if="error" variant="error" title="Lỗi tải thương hiệu">{{ error }}</AppAlert>

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
        <span class="text-sm font-semibold">Đang tải danh sách thương hiệu từ máy chủ…</span>
      </div>

      <!-- Empty State -->
      <div
        v-else-if="brands.length === 0"
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
              d="M7 7h.01M7 3h5c.512 0 1.024.195 1.414.586l7 7a2 2 0 010 2.828l-7 7a2 2 0 01-2.828 0l-7-7A1.994 1.994 0 013 12V7a4 4 0 014-4z"
            />
          </svg>
        </div>
        <h3 class="text-lg font-bold text-white">Chưa có thương hiệu nào</h3>
        <p class="mt-1 text-sm text-slate-400 max-w-md mx-auto">
          Hãy thêm thương hiệu đầu tiên để bắt đầu gán hãng cho từng dòng giày.
        </p>
        <div class="mt-5">
          <BaseButton
            size="sm"
            class="rounded-xl bg-emerald-500 font-bold uppercase tracking-wider text-slate-950 hover:bg-emerald-400 shadow-[0_0_20px_rgba(16,185,129,0.3)]"
            @click="openCreateModal"
          >
            + Thêm thương hiệu đầu tiên
          </BaseButton>
        </div>
      </div>

      <!-- Brands Table -->
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
                <th class="px-6 py-4">Tên Thương Hiệu / Slug</th>
                <th class="px-6 py-4">Mô Tả</th>
                <th class="px-6 py-4">Trạng Thái</th>
                <th class="px-6 py-4 text-right">Thao Tác</th>
              </tr>
            </thead>
            <tbody class="divide-y divide-white/5">
              <tr
                v-for="item in brands"
                :key="item.id"
                class="transition-colors hover:bg-white/[0.02]"
              >
                <td class="px-6 py-4 font-mono text-xs font-bold text-slate-400">#{{ item.id }}</td>
                <td class="px-6 py-4">
                  <div class="font-bold text-white text-base">{{ item.name }}</div>
                  <div class="font-mono text-xs text-emerald-400/80 mt-0.5">{{ item.slug }}</div>
                </td>
                <td class="px-6 py-4 text-xs text-slate-400 max-w-sm">
                  {{ item.description || "Chưa có mô tả" }}
                </td>
                <td class="px-6 py-4">
                  <span
                    :class="[
                      'inline-flex items-center gap-1.5 rounded-full px-2.5 py-1 text-xs font-extrabold uppercase tracking-wider',
                      item.is_active
                        ? 'border border-emerald-500/30 bg-emerald-500/15 text-emerald-400'
                        : 'border border-rose-500/30 bg-rose-500/15 text-rose-400',
                    ]"
                  >
                    {{ item.is_active ? "Hoạt động" : "Đã ẩn" }}
                  </span>
                </td>
                <td class="px-6 py-4 text-right">
                  <div class="flex items-center justify-end gap-2">
                    <button
                      type="button"
                      class="rounded-lg border border-white/10 bg-white/5 px-3 py-1.5 text-xs font-bold text-slate-300 hover:border-emerald-500/30 hover:bg-emerald-500/10 hover:text-emerald-400 transition-colors cursor-pointer"
                      @click="openEditModal(item)"
                    >
                      Sửa
                    </button>
                    <button
                      type="button"
                      class="rounded-lg border border-rose-500/20 bg-rose-500/10 px-3 py-1.5 text-xs font-bold text-rose-400 hover:bg-rose-500/20 transition-colors cursor-pointer"
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

    <!-- Modal Thêm / Sửa Thương Hiệu -->
    <Teleport to="body">
      <Transition name="popup-fade">
        <div
          v-if="showModal"
          class="fixed inset-0 z-50 flex items-center justify-center p-4 sm:p-6"
          role="dialog"
          aria-modal="true"
        >
          <div
            class="fixed inset-0 bg-black/80 backdrop-blur-md transition-opacity"
            aria-hidden="true"
            @click="!submitting && (showModal = false)"
          />

          <div
            class="relative z-10 w-full max-w-md overflow-hidden rounded-3xl border border-white/15 bg-[#12151e] p-6 sm:p-8 text-white shadow-[0_25px_70px_rgba(0,0,0,0.95)]"
          >
            <h2 class="text-xl font-black uppercase tracking-tight text-white mb-2">
              {{ isEditing ? "Chỉnh Sửa Thương Hiệu" : "Thêm Thương Hiệu Mới" }}
            </h2>
            <p class="text-xs text-slate-400 mb-6">
              Hãng sản xuất giày để phân nhóm sản phẩm và size tương ứng.
            </p>

            <AppAlert v-if="formError" variant="error" class="mb-4">{{ formError }}</AppAlert>

            <form class="space-y-4" @submit.prevent="handleFormSubmit">
              <FormField v-slot="field" label="Tên thương hiệu" name="brand-name" required>
                <BaseInput
                  :id="field.id"
                  name="brand_name"
                  :model-value="formData.name"
                  placeholder="Ví dụ: Nike, Adidas, Puma..."
                  required
                  @update:model-value="handleNameChange"
                />
              </FormField>

              <FormField v-slot="field" label="Đường dẫn (Slug)" name="brand-slug" required>
                <BaseInput
                  :id="field.id"
                  name="brand_slug"
                  v-model="formData.slug"
                  placeholder="nike"
                  required
                />
              </FormField>

              <div>
                <label
                  class="block text-xs font-bold uppercase tracking-wider text-slate-300 mb-1.5"
                >
                  Mô tả thương hiệu
                </label>
                <textarea
                  v-model="formData.description"
                  rows="2"
                  placeholder="Mô tả thương hiệu..."
                  class="w-full rounded-xl border border-white/15 bg-white/5 p-3 text-sm text-white placeholder-slate-500 focus:border-emerald-500 focus:outline-none focus:ring-1 focus:ring-emerald-500 transition-colors"
                />
              </div>

              <div class="flex items-center justify-end gap-3 pt-4 border-t border-white/10">
                <BaseButton
                  type="button"
                  variant="ghost"
                  class="rounded-xl border border-white/15 text-slate-300 hover:text-white text-xs font-bold uppercase"
                  :disabled="submitting"
                  @click="showModal = false"
                >
                  Hủy bỏ
                </BaseButton>
                <BaseButton
                  type="submit"
                  class="rounded-xl bg-emerald-500 px-5 text-xs font-black uppercase tracking-wider text-slate-950 hover:bg-emerald-400 shadow-[0_0_20px_rgba(16,185,129,0.3)]"
                  :loading="submitting"
                >
                  {{ isEditing ? "Lưu thay đổi" : "Tạo thương hiệu" }}
                </BaseButton>
              </div>
            </form>
          </div>
        </div>
      </Transition>
    </Teleport>

    <!-- AppPopup Confirm Xóa Thương Hiệu -->
    <AppPopup
      v-model="showDeleteConfirm"
      mode="confirm"
      variant="error"
      title="Xác nhận xóa thương hiệu"
      :message="`Bạn có chắc chắn muốn xóa thương hiệu '${brandToDelete?.name}' (#${brandToDelete?.id})?`"
      action-text="Xóa thương hiệu"
      cancel-text="Hủy"
      :loading="deleteLoading"
      @confirm="confirmDelete"
      @cancel="showDeleteConfirm = false"
    />
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
