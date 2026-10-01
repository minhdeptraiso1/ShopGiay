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
  createAdminColor,
  deleteAdminColor,
  fetchAdminColors,
  updateAdminColor,
  type AdminColor,
  type CreateColorInput,
} from "../api";

const toast = useToastStore();
const colors = ref<AdminColor[]>([]);
const loading = ref(true);
const error = ref("");

// Modal Create / Edit state
const showModal = ref(false);
const isEditing = ref(false);
const editingColorId = ref<number | null>(null);
const submitting = ref(false);
const formError = ref("");

const formData = reactive<{
  name: string;
  slug: string;
  hex_code: string;
  is_active: boolean;
}>({
  name: "",
  slug: "",
  hex_code: "#000000",
  is_active: true,
});

// Delete Confirmation
const showDeleteConfirm = ref(false);
const colorToDelete = ref<AdminColor | null>(null);
const deleteLoading = ref(false);

async function loadColors() {
  loading.value = true;
  error.value = "";
  try {
    colors.value = await fetchAdminColors();
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
  editingColorId.value = null;
  formError.value = "";
  formData.name = "";
  formData.slug = "";
  formData.hex_code = "#000000";
  formData.is_active = true;
  showModal.value = true;
}

function openEditModal(color: AdminColor) {
  isEditing.value = true;
  editingColorId.value = color.id;
  formError.value = "";
  formData.name = color.name;
  formData.slug = color.slug;
  formData.hex_code = color.hex_code || "#000000";
  formData.is_active = color.is_active;
  showModal.value = true;
}

async function handleFormSubmit() {
  if (!formData.name.trim()) {
    formError.value = "Tên màu sắc không được để trống.";
    return;
  }
  if (!formData.slug.trim()) {
    formError.value = "Định danh slug không được để trống.";
    return;
  }

  submitting.value = true;
  formError.value = "";

  try {
    if (isEditing.value && editingColorId.value) {
      const updated = await updateAdminColor(editingColorId.value, {
        name: formData.name.trim(),
        slug: formData.slug.trim(),
        hex_code: formData.hex_code.trim(),
        is_active: formData.is_active,
      });
      const idx = colors.value.findIndex((c) => c.id === updated.id);
      if (idx !== -1) colors.value[idx] = updated;
      toast.show("Cập nhật màu sắc thành công!", "success");
    } else {
      const payload: CreateColorInput = {
        name: formData.name.trim(),
        slug: formData.slug.trim(),
        hex_code: formData.hex_code.trim(),
        is_active: formData.is_active,
      };
      const created = await createAdminColor(payload);
      colors.value.unshift(created);
      toast.show("Tạo màu sắc mới thành công!", "success");
    }
    showModal.value = false;
  } catch (err) {
    formError.value = toAppError(err).message;
  } finally {
    submitting.value = false;
  }
}

function confirmDelete(color: AdminColor) {
  colorToDelete.value = color;
  showDeleteConfirm.value = true;
}

async function handleDelete() {
  if (!colorToDelete.value) return;
  deleteLoading.value = true;
  try {
    await deleteAdminColor(colorToDelete.value.id);
    colors.value = colors.value.filter((c) => c.id !== colorToDelete.value?.id);
    toast.show(`Đã xóa màu ${colorToDelete.value.name}!`, "success");
    showDeleteConfirm.value = false;
  } catch (err) {
    toast.show(toAppError(err).message, "error");
  } finally {
    deleteLoading.value = false;
    colorToDelete.value = null;
  }
}

onMounted(() => {
  loadColors();
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
            Màu Sắc Sản Phẩm (Colors)
          </h1>
          <p class="text-xs sm:text-sm text-slate-400 mt-1">
            Quản lý bảng màu sắc cho giày với mã HEX chuẩn và swatch xem trước.
          </p>
        </div>
        <div class="flex items-center gap-3">
          <BaseButton variant="secondary" size="sm" @click="loadColors"> Làm mới </BaseButton>
          <BaseButton variant="primary" size="sm" class="gap-2" @click="openCreateModal">
            <svg class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path
                stroke-linecap="round"
                stroke-linejoin="round"
                stroke-width="2"
                d="M12 4v16m8-8H4"
              />
            </svg>
            Thêm Màu Mới
          </BaseButton>
        </div>
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
          Đang tải danh sách màu sắc…
        </div>

        <div v-else-if="colors.length === 0" class="p-12 text-center">
          <div
            class="inline-flex h-12 w-12 items-center justify-center rounded-2xl bg-white/5 text-slate-400 mb-3"
          >
            <svg class="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path
                stroke-linecap="round"
                stroke-linejoin="round"
                stroke-width="2"
                d="M7 21a4 4 0 01-4-4V5a2 2 0 012-2h4a2 2 0 012 2v12a4 4 0 01-4 4zm0 0h12a2 2 0 002-2v-4a2 2 0 00-2-2h-2.343M11 7.343l1.657-1.657a2 2 0 012.828 0l2.829 2.829a2 2 0 010 2.828l-8.486 8.485M7 17h.01"
              />
            </svg>
          </div>
          <p class="text-sm font-bold text-white">Chưa có màu sắc nào</p>
          <p class="text-xs text-slate-400 mt-1">Bấm "Thêm Màu Mới" để tạo màu sắc cho sản phẩm.</p>
        </div>

        <table v-else class="w-full text-left text-sm text-slate-300">
          <thead
            class="border-b border-white/10 bg-white/5 text-[11px] font-bold uppercase tracking-wider text-slate-400"
          >
            <tr>
              <th scope="col" class="py-3.5 pl-6 pr-3">ID</th>
              <th scope="col" class="px-3 py-3.5">Màu sắc (Color)</th>
              <th scope="col" class="px-3 py-3.5">Định danh (Slug)</th>
              <th scope="col" class="px-3 py-3.5">Mã Màu (HEX)</th>
              <th scope="col" class="px-3 py-3.5">Trạng thái</th>
              <th scope="col" class="py-3.5 pl-3 pr-6 text-right">Thao tác</th>
            </tr>
          </thead>
          <tbody class="divide-y divide-white/5">
            <tr
              v-for="color in colors"
              :key="color.id"
              class="hover:bg-white/[0.02] transition-colors"
            >
              <td class="whitespace-nowrap py-4 pl-6 pr-3 text-xs font-bold text-slate-400">
                #{{ color.id }}
              </td>
              <td class="whitespace-nowrap px-3 py-4">
                <div class="flex items-center gap-2.5">
                  <span
                    class="h-5 w-5 rounded-full border border-white/20 shadow-sm flex-shrink-0"
                    :style="{ backgroundColor: color.hex_code || '#cccccc' }"
                  />
                  <span class="font-bold text-white">{{ color.name }}</span>
                </div>
              </td>
              <td class="whitespace-nowrap px-3 py-4 text-xs font-mono text-emerald-400">
                {{ color.slug }}
              </td>
              <td class="whitespace-nowrap px-3 py-4 text-xs font-mono text-slate-300">
                {{ color.hex_code || "Chưa đặt" }}
              </td>
              <td class="whitespace-nowrap px-3 py-4 text-xs">
                <span
                  :class="[
                    'inline-flex items-center rounded-md px-2 py-0.5 text-[10px] font-bold uppercase tracking-wider',
                    color.is_active
                      ? 'bg-emerald-500/15 text-emerald-400 border border-emerald-500/30'
                      : 'bg-rose-500/15 text-rose-400 border border-rose-500/30',
                  ]"
                >
                  {{ color.is_active ? "Hoạt động" : "Tạm tắt" }}
                </span>
              </td>
              <td class="whitespace-nowrap py-4 pl-3 pr-6 text-right text-xs">
                <div class="flex items-center justify-end gap-2">
                  <button
                    type="button"
                    class="rounded-lg bg-white/5 px-2.5 py-1.5 font-bold text-slate-300 hover:bg-white/10 hover:text-white transition-all cursor-pointer"
                    @click="openEditModal(color)"
                  >
                    Sửa
                  </button>
                  <button
                    type="button"
                    class="rounded-lg bg-rose-500/10 px-2.5 py-1.5 font-bold text-rose-400 hover:bg-rose-500/20 transition-all cursor-pointer"
                    @click="confirmDelete(color)"
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

    <!-- Create / Edit Color Modal -->
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
              {{ isEditing ? "Cập Nhật Màu Sắc" : "Thêm Màu Mới" }}
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
            <!-- Name -->
            <FormField
              v-slot="field"
              label="Tên màu sắc"
              name="color-name"
              required
              help="Ví dụ: Đen, Trắng, Đỏ Sport, Xanh Neon"
            >
              <BaseInput
                :id="field.id"
                name="color_name"
                :model-value="formData.name"
                placeholder="Xanh Dương Royal"
                required
                @update:model-value="handleNameChange"
              />
            </FormField>

            <!-- Slug -->
            <FormField v-slot="field" label="Đường dẫn định danh (Slug)" name="color-slug" required>
              <BaseInput
                :id="field.id"
                name="color_slug"
                v-model="formData.slug"
                placeholder="xanh-duong-royal"
                required
              />
            </FormField>

            <!-- Hex Code with Visual Picker -->
            <div>
              <label class="block text-xs font-bold uppercase tracking-wider text-slate-300 mb-1.5">
                Mã Màu HEX (#RRGGBB)
              </label>
              <div class="flex items-center gap-3">
                <input
                  type="color"
                  v-model="formData.hex_code"
                  class="h-10 w-12 rounded-xl border border-white/15 bg-white/5 p-1 cursor-pointer"
                />
                <input
                  type="text"
                  v-model="formData.hex_code"
                  placeholder="#000000"
                  maxlength="7"
                  class="flex-1 rounded-xl border border-white/15 bg-white/5 px-3 py-2 text-sm text-white font-mono focus:border-emerald-500 focus:outline-none"
                />
              </div>
            </div>

            <!-- Is Active -->
            <div class="flex items-center gap-2 pt-2">
              <input
                id="color-active"
                v-model="formData.is_active"
                type="checkbox"
                class="h-4 w-4 rounded border-white/20 bg-white/5 text-emerald-500 focus:ring-emerald-500"
              />
              <label
                for="color-active"
                class="text-xs font-bold uppercase tracking-wider text-slate-300 cursor-pointer"
              >
                Màu sắc đang kích hoạt
              </label>
            </div>

            <!-- Action buttons -->
            <div class="mt-6 flex items-center justify-end gap-3 pt-4 border-t border-white/10">
              <BaseButton type="button" variant="secondary" size="sm" @click="showModal = false">
                Hủy bỏ
              </BaseButton>
              <BaseButton type="submit" variant="primary" size="sm" :loading="submitting">
                {{ isEditing ? "Lưu Thay Đổi" : "Tạo Màu Mới" }}
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
      title="Xác nhận xóa màu sắc"
      :message="`Hành động này sẽ xóa màu sắc '${colorToDelete?.name}' khỏi danh mục. Các biến thể đang dùng màu này có thể bị ảnh hưởng.`"
      action-text="Xóa vĩnh viễn"
      cancel-text="Hủy bỏ"
      :loading="deleteLoading"
      @confirm="handleDelete"
      @cancel="showDeleteConfirm = false"
    />
  </AdminLayout>
</template>
