<script setup lang="ts">
import { onMounted, ref } from "vue";

import BaseButton from "@/components/base/BaseButton.vue";
import BaseInput from "@/components/base/BaseInput.vue";
import BasePagination from "@/components/base/BasePagination.vue";
import AppAlert from "@/components/feedback/AppAlert.vue";
import FormField from "@/components/form/FormField.vue";
import AdminLayout from "@/layouts/AdminLayout.vue";
import { toAppError } from "@/lib/http/errors";
import { fetchAuditLogs, type AuditLogItem } from "../api";

const logs = ref<AuditLogItem[]>([]);
const entityType = ref("");
const action = ref("");
const search = ref("");
const startDate = ref("");
const endDate = ref("");
const page = ref(1);
const count = ref(0);
const loading = ref(true);
const errorMessage = ref("");

function actionLabel(value: string): string {
  return (
    {
      created: "Đã tạo",
      updated: "Đã cập nhật",
      deactivated: "Đã vô hiệu hóa",
      adjusted: "Đã điều chỉnh",
      transitioned: "Đã chuyển trạng thái",
      role_changed: "Đã đổi vai trò",
    }[value] ?? value
  );
}

function entityLabel(value: string): string {
  return (
    {
      "catalog.product": "Sản phẩm",
      "catalog.productvariant": "Biến thể SKU",
      "catalog.category": "Danh mục",
      "catalog.brand": "Thương hiệu",
      "catalog.size": "Kích cỡ",
      "catalog.color": "Màu sắc",
      "catalog.productimage": "Ảnh sản phẩm",
      "catalog.stockmovement": "Biến động kho",
      "catalog.inventory": "Tồn kho",
      "catalog.inventorybalance": "Tồn kho",
      "orders.order": "Đơn hàng",
      "engagement.voucher": "Voucher",
      "engagement.banner": "Banner",
      "exchanges.exchangerequest": "Đổi hàng",
      "accounts.user": "Tài khoản",
    }[value] ?? value
  );
}

async function load(resetPage = false): Promise<void> {
  if (resetPage) page.value = 1;
  loading.value = true;
  errorMessage.value = "";
  try {
    const response = await fetchAuditLogs({
      entity_type: entityType.value || undefined,
      action: action.value || undefined,
      search: search.value || undefined,
      start_date: startDate.value || undefined,
      end_date: endDate.value || undefined,
      page: page.value,
    });
    logs.value = response.results;
    count.value = response.count;
  } catch (error) {
    errorMessage.value = toAppError(error).message;
  } finally {
    loading.value = false;
  }
}

async function changePage(next: number): Promise<void> {
  page.value = next;
  await load();
}

async function clearFilters(): Promise<void> {
  search.value = "";
  entityType.value = "";
  action.value = "";
  startDate.value = "";
  endDate.value = "";
  await load(true);
}

onMounted(() => void load());
</script>

<template>
  <AdminLayout>
    <div class="space-y-6">
      <header>
        <p class="text-xs font-black tracking-[0.18em] text-emerald-400 uppercase">Chỉ ghi thêm</p>
        <h1 class="mt-2 text-3xl font-black text-white">Nhật ký kiểm toán</h1>
        <p class="mt-2 text-sm text-slate-400">
          Theo dõi thay đổi vai trò, sản phẩm, tồn kho, đơn hàng, voucher và đổi hàng.
        </p>
      </header>

      <section class="rounded-2xl border border-white/10 bg-[#12151e] p-5">
        <div
          class="grid gap-4 md:grid-cols-2 xl:grid-cols-[minmax(22rem,1.5fr)_minmax(12rem,.8fr)_minmax(10rem,.65fr)_minmax(10rem,.65fr)_minmax(12rem,.8fr)_auto_auto] xl:items-end"
        >
          <FormField v-slot="field" label="Tìm kiếm" name="audit-search">
            <BaseInput
              v-model="search"
              :id="field.id"
              name="search"
              placeholder="Nội dung, người thực hiện, mã đối tượng"
              clearable
              @keyup.enter="load(true)"
            />
          </FormField>
          <FormField v-slot="field" label="Loại đối tượng" name="audit-entity">
            <select
              v-model="entityType"
              :id="field.id"
              name="entity_type"
              class="min-h-12 w-full rounded-xl border border-[var(--color-border)] bg-[var(--color-input-bg)] px-3 text-sm text-[var(--color-text)]"
            >
              <option value="">Tất cả đối tượng</option>
              <option value="catalog.product">Sản phẩm</option>
              <option value="catalog.productvariant">Biến thể SKU</option>
              <option value="catalog.stockmovement">Biến động kho</option>
              <option value="orders.order">Đơn hàng</option>
              <option value="engagement.voucher">Voucher</option>
              <option value="engagement.banner">Banner</option>
              <option value="exchanges.exchangerequest">Đổi hàng</option>
              <option value="accounts.user">Tài khoản</option>
            </select>
          </FormField>
          <FormField v-slot="field" label="Từ ngày" name="audit-start-date">
            <BaseInput v-model="startDate" :id="field.id" name="start_date" type="date" />
          </FormField>
          <FormField v-slot="field" label="Đến ngày" name="audit-end-date">
            <BaseInput v-model="endDate" :id="field.id" name="end_date" type="date" />
          </FormField>
          <FormField v-slot="field" label="Hành động" name="audit-action">
            <select
              v-model="action"
              :id="field.id"
              name="action"
              class="min-h-12 w-full rounded-xl border border-[var(--color-border)] bg-[var(--color-input-bg)] px-3 text-sm text-[var(--color-text)]"
            >
              <option value="">Tất cả hành động</option>
              <option value="created">Đã tạo</option>
              <option value="updated">Đã cập nhật</option>
              <option value="adjusted">Đã điều chỉnh</option>
              <option value="transitioned">Đã chuyển trạng thái</option>
              <option value="deactivated">Đã vô hiệu hóa</option>
              <option value="role_changed">Đã đổi vai trò</option>
            </select>
          </FormField>
          <BaseButton :loading="loading" @click="load(true)">Lọc nhật ký</BaseButton>
          <BaseButton variant="secondary" @click="clearFilters">Xóa bộ lọc</BaseButton>
        </div>
      </section>

      <AppAlert v-if="errorMessage" variant="error" title="Không tải được nhật ký kiểm toán">
        {{ errorMessage }}
      </AppAlert>

      <section class="overflow-hidden rounded-2xl border border-white/10 bg-[#12151e]">
        <div class="flex items-center justify-between border-b border-white/10 p-5">
          <h2 class="text-lg font-black text-white">{{ count }} bản ghi</h2>
          <span class="text-xs text-slate-500">Trang {{ page }}</span>
        </div>
        <div v-if="loading" class="p-8 text-center text-slate-500">Đang tải nhật ký…</div>
        <div v-else class="overflow-x-auto">
          <table class="w-full text-left text-sm">
            <thead class="bg-white/[0.03] text-xs text-slate-500 uppercase">
              <tr>
                <th class="p-4">Thời gian</th>
                <th>Người thực hiện</th>
                <th>Hành động</th>
                <th>Đối tượng</th>
                <th class="pr-4">Nội dung</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="log in logs" :key="log.id" class="border-t border-white/8">
                <td class="p-4 whitespace-nowrap text-slate-400">
                  {{ new Date(log.created_at).toLocaleString("vi-VN") }}
                </td>
                <td>{{ log.actor_email || "Hệ thống" }}</td>
                <td>
                  <span
                    class="rounded-full bg-emerald-500/12 px-2 py-1 text-xs font-bold text-emerald-400"
                    >{{ actionLabel(log.action) }}</span
                  >
                </td>
                <td>
                  <p class="font-mono text-xs text-slate-300">
                    {{ entityLabel(log.entity_type) }} #{{ log.entity_id }}
                  </p>
                </td>
                <td class="pr-4 text-slate-300">{{ log.summary }}</td>
              </tr>
            </tbody>
          </table>
          <p v-if="!logs.length" class="p-8 text-center text-slate-500">
            Không có bản ghi phù hợp.
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
