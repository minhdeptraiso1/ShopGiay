<script setup lang="ts">
import { useField, useForm } from "vee-validate";
import { onMounted, ref } from "vue";

import BaseButton from "@/components/base/BaseButton.vue";
import BaseInput from "@/components/base/BaseInput.vue";
import AppAlert from "@/components/feedback/AppAlert.vue";
import AppPopup from "@/components/feedback/AppPopup.vue";
import FormField from "@/components/form/FormField.vue";
import AppLayout from "@/layouts/AppLayout.vue";
import { useToastStore } from "@/app/stores/toast";
import { toAppError } from "@/lib/http/errors";
import { useAddresses } from "@/modules/addresses/composables/useAddresses";
import { addressSchema } from "@/modules/addresses/schemas";
import type { Address, AddressPayload } from "@/modules/addresses/types";

const EMPTY_FORM = {
  recipientName: "",
  phoneNumber: "",
  province: "",
  district: "",
  ward: "",
  streetAddress: "",
};

const toast = useToastStore();
const {
  addresses,
  loading,
  actionLoading,
  error,
  loadAddresses,
  saveAddress,
  removeAddress,
  makeDefault,
} = useAddresses();

const editingId = ref<number>();
const submitError = ref("");
const addressToDelete = ref<Address | null>(null);
const showDeleteConfirm = ref(false);

const { handleSubmit, resetForm, setFieldError } = useForm({
  validationSchema: addressSchema,
  initialValues: EMPTY_FORM,
});
const { value: recipientName, errorMessage: recipientNameError } =
  useField<string>("recipientName");
const { value: phoneNumber, errorMessage: phoneNumberError } = useField<string>("phoneNumber");
const { value: province, errorMessage: provinceError } = useField<string>("province");
const { value: district, errorMessage: districtError } = useField<string>("district");
const { value: ward, errorMessage: wardError } = useField<string>("ward");
const { value: streetAddress, errorMessage: streetAddressError } =
  useField<string>("streetAddress");

function payloadFromValues(values: typeof EMPTY_FORM): AddressPayload {
  return {
    recipient_name: values.recipientName,
    phone_number: values.phoneNumber,
    province: values.province,
    district: values.district,
    ward: values.ward,
    street_address: values.streetAddress,
  };
}

function beginEdit(address: Address) {
  editingId.value = address.id;
  submitError.value = "";
  resetForm({
    values: {
      recipientName: address.recipient_name,
      phoneNumber: address.phone_number,
      province: address.province,
      district: address.district,
      ward: address.ward,
      streetAddress: address.street_address,
    },
  });
  globalThis.document
    .querySelector("#address-form-heading")
    ?.scrollIntoView({ behavior: "smooth" });
}

function cancelEdit() {
  editingId.value = undefined;
  submitError.value = "";
  resetForm({ values: EMPTY_FORM });
}

const fieldMap: Record<string, keyof typeof EMPTY_FORM> = {
  recipient_name: "recipientName",
  phone_number: "phoneNumber",
  province: "province",
  district: "district",
  ward: "ward",
  street_address: "streetAddress",
};

const submit = handleSubmit(async (values) => {
  submitError.value = "";
  try {
    await saveAddress(payloadFromValues(values), editingId.value);
    toast.show(editingId.value ? "Cập nhật địa chỉ thành công." : "Thêm địa chỉ thành công.", "success");
    cancelEdit();
  } catch (requestError) {
    const appError = toAppError(requestError);
    Object.entries(appError.fields).forEach(([field, message]) => {
      const formField = fieldMap[field];
      if (formField) setFieldError(formField, message);
    });
    if (Object.keys(appError.fields).length === 0) {
      submitError.value = appError.message;
      toast.show(appError.message, "error");
    }
  }
});

function promptDelete(address: Address) {
  addressToDelete.value = address;
  showDeleteConfirm.value = true;
}

async function handleConfirmedDelete() {
  if (!addressToDelete.value) return;
  const targetId = addressToDelete.value.id;
  submitError.value = "";
  try {
    await removeAddress(targetId);
    toast.show("Đã xóa địa chỉ.", "success");
    if (editingId.value === targetId) cancelEdit();
  } catch (requestError) {
    const err = toAppError(requestError).message;
    submitError.value = err;
    toast.show(err, "error");
  } finally {
    showDeleteConfirm.value = false;
    addressToDelete.value = null;
  }
}

async function setDefault(address: Address) {
  submitError.value = "";
  try {
    await makeDefault(address.id);
    toast.show("Đã đặt làm địa chỉ mặc định.", "success");
  } catch (requestError) {
    const err = toAppError(requestError).message;
    submitError.value = err;
    toast.show(err, "error");
  }
}

onMounted(loadAddresses);
</script>

<template>
  <AppLayout>
    <div class="addresses-page grid gap-8 lg:grid-cols-[minmax(0,1.15fr)_minmax(20rem,0.85fr)]">
      <!-- Address List Section -->
      <section aria-labelledby="address-list-heading" class="space-y-6">
        <header class="space-y-1.5">
          <p class="text-xs font-bold uppercase tracking-widest text-emerald-400">Sổ địa chỉ</p>
          <h1 id="address-list-heading" class="text-2xl sm:text-3xl font-black uppercase tracking-tight text-white">
            Địa chỉ nhận hàng
          </h1>
          <p class="text-sm text-slate-400">
            Địa chỉ mặc định sẽ được chọn ưu tiên khi bạn đặt mua các sản phẩm giày thể thao.
          </p>
        </header>

        <AppAlert v-if="error" variant="error" title="Không thể tải địa chỉ">{{ error }}</AppAlert>

        <div v-if="loading" class="flex items-center justify-center p-12 text-slate-400" role="status">
          <svg class="h-6 w-6 animate-spin text-emerald-400 mr-3" viewBox="0 0 24 24" fill="none">
            <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4" />
            <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8v8H4z" />
          </svg>
          <span class="text-sm font-semibold">Đang tải danh sách địa chỉ…</span>
        </div>

        <div
          v-else-if="addresses.length === 0"
          class="rounded-3xl border border-dashed border-white/15 bg-white/5 p-8 text-center"
        >
          <div class="mx-auto mb-3 flex h-12 w-12 items-center justify-center rounded-2xl bg-white/5 text-slate-400">
            <svg class="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M17.657 16.657L13.414 20.9a1.998 1.998 0 01-2.827 0l-4.244-4.243a8 8 0 1111.314 0z" />
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M15 11a3 3 0 11-6 0 3 3 0 016 0z" />
            </svg>
          </div>
          <p class="font-bold text-white">Bạn chưa có địa chỉ nhận hàng nào.</p>
          <p class="mt-1 text-sm text-slate-400">
            Điền biểu mẫu bên cạnh để tạo địa chỉ giao hàng đầu tiên.
          </p>
        </div>

        <ul v-else class="space-y-4">
          <li
            v-for="address in addresses"
            :key="address.id"
            :class="[
              'rounded-3xl border p-5 sm:p-6 transition-all backdrop-blur-xl shadow-lg',
              address.is_default
                ? 'border-emerald-500/50 bg-[#121722]/90 shadow-[0_10px_30px_rgba(16,185,129,0.1)]'
                : 'border-white/10 bg-[#12151e]/85 hover:border-white/20'
            ]"
          >
            <div class="flex flex-wrap items-start justify-between gap-3">
              <div>
                <div class="flex flex-wrap items-center gap-2">
                  <h2 class="font-black text-white text-base sm:text-lg">{{ address.recipient_name }}</h2>
                  <span
                    v-if="address.is_default"
                    class="rounded-full bg-emerald-500/15 border border-emerald-500/30 px-2.5 py-0.5 text-xs font-bold uppercase tracking-wider text-emerald-400"
                  >
                    Mặc định
                  </span>
                </div>
                <p class="mt-1 text-xs sm:text-sm font-semibold text-emerald-400/90">
                  {{ address.phone_number }}
                </p>
                <address class="mt-2.5 text-sm leading-relaxed text-slate-300 not-italic">
                  {{ address.street_address }}, {{ address.ward }}, {{ address.district }},
                  {{ address.province }}
                </address>
              </div>

              <!-- Action Buttons -->
              <div class="flex flex-wrap gap-2">
                <BaseButton
                  size="sm"
                  variant="ghost"
                  class="rounded-xl border border-white/15 text-slate-300 hover:text-white text-xs font-bold"
                  @click="beginEdit(address)"
                >
                  Sửa
                </BaseButton>
                <BaseButton
                  size="sm"
                  variant="ghost"
                  class="rounded-xl border border-rose-500/20 bg-rose-500/10 text-rose-400 hover:bg-rose-500/20 text-xs font-bold"
                  @click="promptDelete(address)"
                >
                  Xóa
                </BaseButton>
              </div>
            </div>

            <div v-if="!address.is_default" class="mt-4 pt-3 border-t border-white/5">
              <BaseButton
                size="sm"
                variant="ghost"
                class="text-xs font-bold text-slate-400 hover:text-emerald-400"
                :loading="actionLoading"
                @click="setDefault(address)"
              >
                + Đặt làm địa chỉ mặc định
              </BaseButton>
            </div>
          </li>
        </ul>
      </section>

      <!-- Form Section (Create / Edit) -->
      <section
        class="self-start rounded-3xl border border-white/10 bg-[#12151e]/85 backdrop-blur-xl p-6 sm:p-8 shadow-[0_25px_60px_-15px_rgba(0,0,0,0.9)] lg:sticky lg:top-24"
      >
        <h2 id="address-form-heading" class="text-xl font-black uppercase tracking-tight text-white">
          {{ editingId ? "Cập nhật địa chỉ" : "Thêm địa chỉ mới" }}
        </h2>
        <p class="mt-1 text-xs text-slate-400">
          {{ editingId ? "Chỉnh sửa thông tin địa chỉ đã lưu." : "Nhập đầy đủ thông tin để giao hàng chuẩn xác." }}
        </p>

        <form class="mt-6 space-y-4" novalidate @submit.prevent="submit">
          <FormField
            v-slot="field"
            label="Họ và tên người nhận"
            name="recipientName"
            :error="recipientNameError"
            required
          >
            <BaseInput
              v-model="recipientName"
              :id="field.id"
              name="recipient_name"
              autocomplete="name"
              placeholder="VD: Nguyễn Văn A"
              :invalid="field.invalid"
              :aria-describedby="field.describedBy"
              required
            />
          </FormField>

          <FormField
            v-slot="field"
            label="Số điện thoại"
            name="phoneNumber"
            :error="phoneNumberError"
            required
          >
            <BaseInput
              v-model="phoneNumber"
              :id="field.id"
              name="phone_number"
              autocomplete="tel"
              placeholder="VD: 0912345678"
              :invalid="field.invalid"
              :aria-describedby="field.describedBy"
              required
            />
          </FormField>

          <div class="grid gap-3 sm:grid-cols-2">
            <FormField
              v-slot="field"
              label="Tỉnh/Thành phố"
              name="province"
              :error="provinceError"
              required
            >
              <BaseInput
                v-model="province"
                :id="field.id"
                name="province"
                autocomplete="address-level1"
                placeholder="Hà Nội"
                :invalid="field.invalid"
                :aria-describedby="field.describedBy"
                required
              />
            </FormField>
            <FormField
              v-slot="field"
              label="Quận/Huyện"
              name="district"
              :error="districtError"
              required
            >
              <BaseInput
                v-model="district"
                :id="field.id"
                name="district"
                autocomplete="address-level2"
                placeholder="Cầu Giấy"
                :invalid="field.invalid"
                :aria-describedby="field.describedBy"
                required
              />
            </FormField>
          </div>

          <FormField v-slot="field" label="Phường/Xã" name="ward" :error="wardError" required>
            <BaseInput
              v-model="ward"
              :id="field.id"
              name="ward"
              autocomplete="address-level3"
              placeholder="Dịch Vọng Hậu"
              :invalid="field.invalid"
              :aria-describedby="field.describedBy"
              required
            />
          </FormField>

          <FormField
            v-slot="field"
            label="Địa chỉ chi tiết (Số nhà, ngõ, đường)"
            name="streetAddress"
            :error="streetAddressError"
            required
          >
            <BaseInput
              v-model="streetAddress"
              :id="field.id"
              name="street_address"
              autocomplete="street-address"
              placeholder="Số 123 Đường Cầu Giấy"
              :invalid="field.invalid"
              :aria-describedby="field.describedBy"
              required
            />
          </FormField>

          <div class="flex flex-wrap items-center justify-end gap-3 pt-2">
            <BaseButton
              v-if="editingId"
              type="button"
              variant="ghost"
              class="rounded-xl border border-white/15 text-slate-300 hover:bg-white/10 text-xs font-bold uppercase tracking-wider"
              @click="cancelEdit"
            >
              Hủy
            </BaseButton>
            <BaseButton
              type="submit"
              class="min-h-11 px-6 rounded-xl text-xs sm:text-sm font-black uppercase tracking-wider shadow-[0_8px_20px_rgba(16,185,129,0.3)]"
              :loading="actionLoading"
            >
              {{ editingId ? "Lưu thay đổi" : "Thêm địa chỉ" }}
            </BaseButton>
          </div>
        </form>
      </section>
    </div>

    <!-- Confirm Delete Modal using AppPopup -->
    <AppPopup
      v-model="showDeleteConfirm"
      mode="confirm"
      variant="error"
      title="Xác nhận xóa địa chỉ"
      :message="`Bạn có chắc chắn muốn xóa địa chỉ nhận hàng của '${addressToDelete?.recipient_name}'?`"
      action-text="Xóa vĩnh viễn"
      cancel-text="Giữ lại"
      :loading="actionLoading"
      @confirm="handleConfirmedDelete"
    />
  </AppLayout>
</template>

<style scoped>
.addresses-page {
  --color-input-bg: #0b0e14;
  --color-border: rgba(255, 255, 255, 0.15);
  --color-text: #ffffff;
  --color-text-muted: #94a3b8;
}
</style>
