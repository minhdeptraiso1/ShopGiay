<script setup lang="ts">
import { onMounted, reactive, ref } from "vue";

import BaseButton from "@/components/base/BaseButton.vue";
import BaseDialog from "@/components/base/BaseDialog.vue";
import BaseInput from "@/components/base/BaseInput.vue";
import BasePagination from "@/components/base/BasePagination.vue";
import AppAlert from "@/components/feedback/AppAlert.vue";
import FormField from "@/components/form/FormField.vue";
import AdminLayout from "@/layouts/AdminLayout.vue";
import { toAppError } from "@/lib/http/errors";
import { createStaff, fetchStaff, updateStaff, type StaffAccount } from "../api";

const staff = ref<StaffAccount[]>([]);
const loading = ref(true);
const submitting = ref(false);
const errorMessage = ref("");
const successMessage = ref("");
const createOpen = ref(false);
const search = ref("");
const status = ref("all");
const page = ref(1);
const count = ref(0);
const form = reactive({ email: "", full_name: "", password: "" });

async function loadStaff(): Promise<void> {
  loading.value = true;
  errorMessage.value = "";
  try {
    const response = await fetchStaff({
      page: page.value,
      search: search.value || undefined,
      is_active: status.value === "all" ? undefined : status.value === "active",
    });
    staff.value = response.results;
    count.value = response.count;
  } catch (error) {
    errorMessage.value = toAppError(error).message;
  } finally {
    loading.value = false;
  }
}

async function submit(): Promise<void> {
  submitting.value = true;
  errorMessage.value = "";
  successMessage.value = "";
  try {
    await createStaff({ ...form });
    await loadStaff();
    form.email = "";
    form.full_name = "";
    form.password = "";
    successMessage.value = "Đã tạo tài khoản STAFF. Tài khoản không thể tự nâng lên ADMIN.";
    createOpen.value = false;
  } catch (error) {
    errorMessage.value = toAppError(error).message;
  } finally {
    submitting.value = false;
  }
}

async function toggleActive(account: StaffAccount): Promise<void> {
  errorMessage.value = "";
  try {
    const updated = await updateStaff(account.id, { is_active: !account.is_active });
    staff.value = staff.value.map((item) => (item.id === updated.id ? updated : item));
  } catch (error) {
    errorMessage.value = toAppError(error).message;
  }
}

onMounted(loadStaff);

async function applyFilters(): Promise<void> {
  page.value = 1;
  await loadStaff();
}

async function clearFilters(): Promise<void> {
  search.value = "";
  status.value = "all";
  await applyFilters();
}

async function changePage(value: number): Promise<void> {
  page.value = value;
  await loadStaff();
}
</script>

<template>
  <AdminLayout>
    <div class="space-y-6">
      <header class="flex flex-wrap items-end justify-between gap-4">
        <div>
          <p class="text-xs font-black tracking-[0.18em] text-emerald-400 uppercase">Phân quyền</p>
          <h1 class="mt-2 text-3xl font-black text-white">Quản lý nhân viên</h1>
          <p class="mt-2 text-sm text-slate-400">
            Tạo, khóa hoặc kích hoạt lại tài khoản STAFF. Chỉ ADMIN truy cập màn này.
          </p>
        </div>
        <BaseButton @click="createOpen = true">Thêm nhân viên</BaseButton>
      </header>

      <AppAlert v-if="errorMessage" variant="error" title="Không thực hiện được">
        {{ errorMessage }}
      </AppAlert>
      <AppAlert v-if="successMessage" variant="success" title="Hoàn tất">
        {{ successMessage }}
      </AppAlert>

      <BaseDialog
        v-model="createOpen"
        title="Thêm nhân viên"
        description="Tạo tài khoản STAFF mới. Có thể khóa tài khoản sau khi tạo."
        :busy="submitting"
      >
        <form class="grid gap-4" @submit.prevent="submit">
          <FormField v-slot="field" label="Họ tên" name="staff-name" required>
            <BaseInput
              v-model="form.full_name"
              :id="field.id"
              name="full_name"
              :invalid="field.invalid"
              :aria-describedby="field.describedBy"
              required
            />
          </FormField>
          <FormField v-slot="field" label="Email" name="staff-email" required>
            <BaseInput
              v-model="form.email"
              :id="field.id"
              name="email"
              type="email"
              autocomplete="email"
              :invalid="field.invalid"
              :aria-describedby="field.describedBy"
              required
            />
          </FormField>
          <FormField v-slot="field" label="Mật khẩu ban đầu" name="staff-password" required>
            <BaseInput
              v-model="form.password"
              :id="field.id"
              name="password"
              type="password"
              autocomplete="new-password"
              :invalid="field.invalid"
              :aria-describedby="field.describedBy"
              required
            />
          </FormField>
          <div class="flex justify-end gap-3 border-t border-white/10 pt-5">
            <BaseButton type="button" variant="secondary" @click="createOpen = false"
              >Hủy</BaseButton
            >
            <BaseButton type="submit" :loading="submitting">Tạo nhân viên</BaseButton>
          </div>
        </form>
      </BaseDialog>

      <section class="rounded-2xl border border-white/10 bg-[#12151e] p-5">
        <div class="grid gap-4 md:grid-cols-[minmax(22rem,1fr)_220px_auto_auto] md:items-end">
          <FormField v-slot="field" label="Tìm nhân viên" name="staff-search">
            <BaseInput
              v-model="search"
              :id="field.id"
              name="search"
              placeholder="Tên hoặc email"
              clearable
              @keyup.enter="applyFilters"
            />
          </FormField>
          <label class="grid gap-2 text-xs font-bold text-slate-300">
            Trạng thái
            <select
              v-model="status"
              class="min-h-12 rounded-xl border border-[var(--color-border)] bg-[var(--color-input-bg)] px-3 text-sm text-[var(--color-text)]"
            >
              <option value="all">Tất cả</option>
              <option value="active">Đang hoạt động</option>
              <option value="inactive">Đã khóa</option>
            </select>
          </label>
          <BaseButton :loading="loading" @click="applyFilters">Lọc danh sách</BaseButton>
          <BaseButton variant="secondary" @click="clearFilters">Xóa bộ lọc</BaseButton>
        </div>
      </section>

      <section class="overflow-hidden rounded-2xl border border-white/10 bg-[#12151e]">
        <div class="border-b border-white/10 p-5">
          <h2 class="text-lg font-black text-white">Danh sách nhân viên</h2>
        </div>
        <div v-if="loading" class="p-8 text-center text-slate-500">Đang tải nhân viên…</div>
        <div v-else class="overflow-x-auto">
          <table class="w-full text-left text-sm">
            <thead class="bg-white/[0.03] text-xs text-slate-500 uppercase">
              <tr>
                <th class="p-4">Nhân viên</th>
                <th>Ngày tạo</th>
                <th>Đăng nhập cuối</th>
                <th>Trạng thái</th>
                <th class="pr-4 text-right">Thao tác</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="account in staff" :key="account.id" class="border-t border-white/8">
                <td class="p-4">
                  <p class="font-bold text-white">{{ account.full_name }}</p>
                  <p class="text-xs text-slate-500">{{ account.email }}</p>
                </td>
                <td>{{ new Date(account.date_joined).toLocaleDateString("vi-VN") }}</td>
                <td>
                  {{
                    account.last_login
                      ? new Date(account.last_login).toLocaleString("vi-VN")
                      : "Chưa đăng nhập"
                  }}
                </td>
                <td>
                  <span :class="account.is_active ? 'text-emerald-400' : 'text-rose-400'">{{
                    account.is_active ? "Đang hoạt động" : "Đã khóa"
                  }}</span>
                </td>
                <td class="pr-4 text-right">
                  <BaseButton
                    size="sm"
                    :variant="account.is_active ? 'danger' : 'secondary'"
                    @click="toggleActive(account)"
                    >{{ account.is_active ? "Khóa" : "Kích hoạt" }}</BaseButton
                  >
                </td>
              </tr>
            </tbody>
          </table>
          <p v-if="!staff.length" class="p-8 text-center text-slate-500">
            Chưa có tài khoản STAFF.
          </p>
        </div>
        <div class="border-t border-white/10 p-4">
          <BasePagination
            :count="count"
            :page="page"
            :disabled="loading"
            @update:page="changePage"
          />
        </div>
      </section>
    </div>
  </AdminLayout>
</template>
