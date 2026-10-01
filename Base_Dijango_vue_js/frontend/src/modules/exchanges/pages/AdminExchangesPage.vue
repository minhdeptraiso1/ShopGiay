<script setup lang="ts">
import { computed, onMounted, reactive, ref, watch } from "vue";

import { useToastStore } from "@/app/stores/toast";
import BaseButton from "@/components/base/BaseButton.vue";
import BaseInput from "@/components/base/BaseInput.vue";
import BaseTextarea from "@/components/base/BaseTextarea.vue";
import AppAlert from "@/components/feedback/AppAlert.vue";
import FormField from "@/components/form/FormField.vue";
import AdminLayout from "@/layouts/AdminLayout.vue";
import { toAppError } from "@/lib/http/errors";
import { fetchAdminExchanges, transitionAdminExchange } from "../api";
import { exchangeStatusClass, exchangeStatusLabels } from "../status";
import type { ExchangeRequest, ExchangeTransitionInput } from "../types";

const toast = useToastStore();
const exchanges = ref<ExchangeRequest[]>([]);
const loading = ref(true);
const saving = ref(false);
const error = ref("");
const statusFilter = ref("");
const selected = ref<ExchangeRequest | null>(null);
const note = ref("");
const trackingNumber = ref("");
const receiveQuantities = reactive<Record<number, string>>({});
const acceptedQuantities = reactive<Record<number, string>>({});
const dispositions = reactive<Record<number, "restock" | "damaged">>({});
const inspectionNotes = reactive<Record<number, string>>({});

const actionHint = computed(() => {
  if (!selected.value) return "Chọn một yêu cầu để xử lý.";
  const labels: Record<string, string> = {
    pending: "Kiểm tra điều kiện và tồn biến thể mới trước khi duyệt.",
    approved: "Nhập số lượng hàng thực tế shop đã nhận.",
    received: "Kiểm tra từng sản phẩm: hàng đạt mới được nhập lại tồn.",
    inspected: "Chuẩn bị giao biến thể thay thế và nhập mã vận đơn nếu có.",
    replacement_ready: "Bàn giao sản phẩm thay thế cho đơn vị vận chuyển.",
    replacement_shipped: "Đang chờ khách xác nhận đã nhận sản phẩm đổi.",
  };
  return labels[selected.value.status] ?? "Yêu cầu đã kết thúc.";
});

async function load(): Promise<void> {
  loading.value = true;
  error.value = "";
  try {
    exchanges.value = await fetchAdminExchanges(statusFilter.value);
    if (selected.value) {
      selected.value = exchanges.value.find((item) => item.id === selected.value?.id) ?? null;
    }
  } catch (err) {
    error.value = toAppError(err).message;
  } finally {
    loading.value = false;
  }
}

function choose(item: ExchangeRequest): void {
  selected.value = item;
  note.value = "";
  trackingNumber.value = item.tracking_number;
  item.items.forEach((line) => {
    receiveQuantities[line.id] = String(line.quantity);
    acceptedQuantities[line.id] = String(line.received_quantity || line.quantity);
    dispositions[line.id] = "restock";
    inspectionNotes[line.id] = "";
  });
}

async function transition(action: ExchangeTransitionInput["action"]): Promise<void> {
  if (!selected.value) return;
  saving.value = true;
  const payload: ExchangeTransitionInput = {
    action,
    expected_updated_at: selected.value.updated_at,
    note: note.value.trim() || undefined,
  };
  if (action === "receive") {
    payload.received_items = selected.value.items.map((item) => ({
      item_id: item.id,
      received_quantity: Number(receiveQuantities[item.id]) || 0,
    }));
  }
  if (action === "inspect") {
    payload.inspected_items = selected.value.items.map((item) => ({
      item_id: item.id,
      accepted_quantity: Number(acceptedQuantities[item.id]) || 0,
      disposition: dispositions[item.id] ?? "damaged",
      inspection_note: inspectionNotes[item.id] || undefined,
    }));
  }
  if (action === "prepare" || action === "ship") {
    payload.tracking_number = trackingNumber.value.trim() || undefined;
  }
  try {
    const updated = await transitionAdminExchange(selected.value.id, payload);
    const index = exchanges.value.findIndex((item) => item.id === updated.id);
    if (index >= 0) exchanges.value[index] = updated;
    choose(updated);
    toast.show(`Đã cập nhật yêu cầu EX-${String(updated.id)}.`, "success");
  } catch (err) {
    toast.show(toAppError(err).message, "error");
  } finally {
    saving.value = false;
  }
}

watch(statusFilter, () => void load());
onMounted(() => void load());
</script>

<template>
  <AdminLayout>
    <div class="space-y-6">
      <header class="flex flex-wrap items-end justify-between gap-4 border-b border-white/10 pb-6">
        <div>
          <p class="text-xs font-black tracking-[0.2em] text-emerald-400 uppercase">Hậu mãi</p>
          <h1 class="mt-2 text-3xl font-black text-white">Quản lý đổi hàng</h1>
          <p class="mt-2 text-sm text-slate-400">
            Duyệt, nhận, kiểm hàng và giao đúng biến thể thay thế. Không xử lý hoàn tiền.
          </p>
        </div>
        <div class="flex flex-wrap gap-2">
          <BaseButton
            v-for="option in [
              { value: '', label: 'Tất cả' },
              { value: 'pending', label: 'Chờ duyệt' },
              { value: 'approved', label: 'Chờ nhận' },
              { value: 'received', label: 'Chờ kiểm' },
              { value: 'replacement_ready', label: 'Sẵn sàng giao' },
              { value: 'replacement_shipped', label: 'Đang giao đổi' },
            ]"
            :key="option.value"
            size="sm"
            :variant="statusFilter === option.value ? 'primary' : 'secondary'"
            @click="statusFilter = option.value"
            >{{ option.label }}</BaseButton
          >
        </div>
      </header>
      <AppAlert v-if="error" variant="error" title="Không tải được yêu cầu">{{ error }}</AppAlert>
      <p v-else-if="loading" class="py-16 text-center text-slate-400">Đang tải yêu cầu đổi hàng…</p>
      <div v-else class="grid gap-6 xl:grid-cols-[minmax(0,1fr)_28rem]">
        <section class="space-y-3">
          <button
            v-for="item in exchanges"
            :key="item.id"
            type="button"
            class="w-full rounded-2xl border bg-[#12151e] p-5 text-left transition"
            :class="
              selected?.id === item.id
                ? 'border-emerald-500/50'
                : 'border-white/10 hover:border-white/20'
            "
            @click="choose(item)"
          >
            <div class="flex justify-between gap-3">
              <div>
                <p class="font-mono text-xs text-slate-500">
                  EX-{{ item.id }} · {{ item.order_number }}
                </p>
                <p class="mt-1 font-black text-white">{{ item.customer_email }}</p>
                <p class="mt-1 text-sm text-slate-400">{{ item.reason }}</p>
              </div>
              <span
                class="h-fit rounded-full px-2.5 py-1 text-[10px] font-black uppercase"
                :class="exchangeStatusClass(item.status)"
                >{{ exchangeStatusLabels[item.status] }}</span
              >
            </div>
            <p class="mt-4 text-xs text-slate-500">
              {{ item.items.length }} dòng sản phẩm ·
              {{ new Date(item.created_at).toLocaleString("vi-VN") }}
            </p>
          </button>
          <p
            v-if="!exchanges.length"
            class="rounded-2xl border border-dashed border-white/15 p-10 text-center text-sm text-slate-500"
          >
            Không có yêu cầu phù hợp.
          </p>
        </section>

        <aside
          class="h-fit rounded-3xl border border-white/10 bg-[#12151e] p-5 xl:sticky xl:top-24"
        >
          <template v-if="selected"
            ><div class="flex items-start justify-between gap-3">
              <div>
                <p class="font-mono text-xs text-emerald-400">EX-{{ selected.id }}</p>
                <h2 class="mt-1 text-xl font-black text-white">Xử lý yêu cầu</h2>
              </div>
              <span
                class="rounded-full px-2.5 py-1 text-[10px] font-black uppercase"
                :class="exchangeStatusClass(selected.status)"
                >{{ exchangeStatusLabels[selected.status] }}</span
              >
            </div>
            <p class="mt-3 text-xs leading-5 text-slate-400">{{ actionHint }}</p>
            <div class="mt-5 space-y-4 border-t border-white/10 pt-4">
              <article
                v-for="item in selected.items"
                :key="item.id"
                class="rounded-xl bg-white/[0.04] p-3"
              >
                <p class="text-sm font-bold text-white">{{ item.product_name }}</p>
                <p class="mt-1 text-xs text-slate-400">
                  {{ item.source_size }}/{{ item.source_color }} →
                  <span class="text-emerald-400"
                    >{{ item.target_size }}/{{ item.target_color }}</span
                  >
                  · SL {{ item.quantity }}
                </p>
                <FormField
                  v-if="selected.status === 'approved'"
                  v-slot="field"
                  class="mt-3"
                  label="Số lượng thực nhận"
                  :name="`received-${item.id}`"
                  ><BaseInput
                    :model-value="receiveQuantities[item.id] ?? ''"
                    :id="field.id"
                    :name="`received_${item.id}`"
                    type="number"
                    min="0"
                    :max="item.quantity"
                    @update:model-value="receiveQuantities[item.id] = $event"
                /></FormField>
                <div v-if="selected.status === 'received'" class="mt-3 space-y-3">
                  <FormField
                    v-slot="field"
                    label="Số lượng đạt kiểm tra"
                    :name="`accepted-${item.id}`"
                    ><BaseInput
                      :model-value="acceptedQuantities[item.id] ?? ''"
                      :id="field.id"
                      :name="`accepted_${item.id}`"
                      type="number"
                      min="0"
                      :max="item.received_quantity"
                      @update:model-value="acceptedQuantities[item.id] = $event"
                  /></FormField>
                  <div class="flex gap-2">
                    <BaseButton
                      size="sm"
                      :variant="dispositions[item.id] === 'restock' ? 'primary' : 'secondary'"
                      @click="dispositions[item.id] = 'restock'"
                      >Đạt / nhập lại kho</BaseButton
                    ><BaseButton
                      size="sm"
                      :variant="dispositions[item.id] === 'damaged' ? 'danger' : 'secondary'"
                      @click="
                        dispositions[item.id] = 'damaged';
                        acceptedQuantities[item.id] = '0';
                      "
                      >Hàng lỗi</BaseButton
                    >
                  </div>
                  <FormField
                    v-slot="field"
                    label="Ghi chú kiểm hàng"
                    :name="`inspection-${item.id}`"
                    ><BaseTextarea
                      :model-value="inspectionNotes[item.id] ?? ''"
                      :id="field.id"
                      :name="`inspection_${item.id}`"
                      :rows="2"
                      @update:model-value="inspectionNotes[item.id] = $event"
                  /></FormField>
                </div>
              </article>
            </div>
            <FormField
              v-if="selected.status === 'inspected' || selected.status === 'replacement_ready'"
              v-slot="field"
              class="mt-4"
              label="Mã vận đơn giao đổi"
              name="tracking"
              ><BaseInput
                v-model="trackingNumber"
                :id="field.id"
                name="tracking_number" /></FormField
            ><FormField v-slot="field" class="mt-4" label="Ghi chú nội bộ" name="staff-note"
              ><BaseTextarea v-model="note" :id="field.id" name="staff_note" :rows="2"
            /></FormField>
            <div class="mt-5 flex flex-wrap gap-2">
              <template v-if="selected.status === 'pending'"
                ><BaseButton :loading="saving" @click="transition('approve')"
                  >Duyệt & giữ tồn</BaseButton
                ><BaseButton variant="danger" :disabled="saving" @click="transition('reject')"
                  >Từ chối</BaseButton
                ></template
              ><template v-else-if="selected.status === 'approved'"
                ><BaseButton :loading="saving" @click="transition('receive')"
                  >Xác nhận nhận hàng</BaseButton
                ><BaseButton variant="danger" :disabled="saving" @click="transition('reject')"
                  >Từ chối</BaseButton
                ></template
              ><BaseButton
                v-else-if="selected.status === 'received'"
                :loading="saving"
                @click="transition('inspect')"
                >Lưu kiểm hàng</BaseButton
              ><BaseButton
                v-else-if="selected.status === 'inspected'"
                :loading="saving"
                @click="transition('prepare')"
                >Sẵn sàng giao đổi</BaseButton
              ><BaseButton
                v-else-if="selected.status === 'replacement_ready'"
                :loading="saving"
                @click="transition('ship')"
                >Bắt đầu giao hàng đổi</BaseButton
              >
            </div></template
          >
          <p v-else class="py-12 text-center text-sm text-slate-500">
            Chọn yêu cầu ở danh sách bên trái.
          </p>
        </aside>
      </div>
    </div>
  </AdminLayout>
</template>
