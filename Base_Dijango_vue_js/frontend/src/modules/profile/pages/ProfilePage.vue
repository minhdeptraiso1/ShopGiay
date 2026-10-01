<script setup lang="ts">
import { storeToRefs } from "pinia";
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
import { useAuthStore } from "@/modules/auth/stores/auth";
import { useProfile } from "@/modules/profile/composables/useProfile";
import { profileSchema } from "@/modules/profile/schemas";

// --- Profile Section ---
const auth = useAuthStore();
const toast = useToastStore();
const { user } = storeToRefs(auth);
const { loading: profileLoading, error: profileError, updateProfile } = useProfile();
const profileSubmitError = ref("");

const { handleSubmit: handleProfileSubmit } = useForm({
  validationSchema: profileSchema,
  initialValues: { fullName: user.value?.full_name || "" },
});
const { value: fullName, errorMessage: fullNameError, handleBlur: blurFullName } =
  useField<string>("fullName");

const submitProfile = handleProfileSubmit(async (values) => {
  profileSubmitError.value = "";
  try {
    await updateProfile(values.fullName);
  } catch {
    profileSubmitError.value = profileError.value;
    toast.show(profileError.value || "Không thể cập nhật họ tên.", "error");
  }
});

// --- Address Section ---
const EMPTY_ADDRESS_FORM = {
  recipientName: "",
  phoneNumber: "",
  province: "",
  district: "",
  ward: "",
  streetAddress: "",
};

const {
  addresses,
  loading: addressesLoading,
  actionLoading: addressActionLoading,
  error: addressesLoadError,
  loadAddresses,
  saveAddress,
  removeAddress,
  makeDefault,
} = useAddresses();

const editingAddressId = ref<number>();
const addressSubmitError = ref("");
const addressToDelete = ref<Address | null>(null);
const showDeleteConfirm = ref(false);

const { handleSubmit: handleAddressSubmit, resetForm: resetAddressForm, setFieldError: setAddressFieldError } = useForm({
  validationSchema: addressSchema,
  initialValues: EMPTY_ADDRESS_FORM,
});

const { value: recipientName, errorMessage: recipientNameError } = useField<string>("recipientName");
const { value: phoneNumber, errorMessage: phoneNumberError } = useField<string>("phoneNumber");
const { value: province, errorMessage: provinceError } = useField<string>("province");
const { value: district, errorMessage: districtError } = useField<string>("district");
const { value: ward, errorMessage: wardError } = useField<string>("ward");
const { value: streetAddress, errorMessage: streetAddressError } = useField<string>("streetAddress");

function payloadFromValues(values: typeof EMPTY_ADDRESS_FORM): AddressPayload {
  return {
    recipient_name: values.recipientName,
    phone_number: values.phoneNumber,
    province: values.province,
    district: values.district,
    ward: values.ward,
    street_address: values.streetAddress,
  };
}

function beginEditAddress(addr: Address) {
  editingAddressId.value = addr.id;
  addressSubmitError.value = "";
  resetAddressForm({
    values: {
      recipientName: addr.recipient_name,
      phoneNumber: addr.phone_number,
      province: addr.province,
      district: addr.district,
      ward: addr.ward,
      streetAddress: addr.street_address,
    },
  });
  globalThis.document.querySelector("#address-form-box")?.scrollIntoView({ behavior: "smooth" });
}

function cancelEditAddress() {
  editingAddressId.value = undefined;
  addressSubmitError.value = "";
  resetAddressForm({ values: EMPTY_ADDRESS_FORM });
}

const addressFieldMap: Record<string, keyof typeof EMPTY_ADDRESS_FORM> = {
  recipient_name: "recipientName",
  phone_number: "phoneNumber",
  province: "province",
  district: "district",
  ward: "ward",
  street_address: "streetAddress",
};

const submitAddress = handleAddressSubmit(async (values) => {
  addressSubmitError.value = "";
  try {
    await saveAddress(payloadFromValues(values), editingAddressId.value);
    toast.show(
      editingAddressId.value ? "Cập nhật địa chỉ thành công." : "Thêm địa chỉ nhận hàng thành công.",
      "success"
    );
    cancelEditAddress();
  } catch (requestError) {
    const appError = toAppError(requestError);
    Object.entries(appError.fields).forEach(([field, message]) => {
      const formField = addressFieldMap[field];
      if (formField) setAddressFieldError(formField, message);
    });
    if (Object.keys(appError.fields).length === 0) {
      addressSubmitError.value = appError.message;
      toast.show(appError.message, "error");
    }
  }
});

function promptDeleteAddress(addr: Address) {
  addressToDelete.value = addr;
  showDeleteConfirm.value = true;
}

async function handleConfirmedDeleteAddress() {
  if (!addressToDelete.value) return;
  const targetId = addressToDelete.value.id;
  addressSubmitError.value = "";
  try {
    await removeAddress(targetId);
    toast.show("Đã xóa địa chỉ thành công.", "success");
    if (editingAddressId.value === targetId) cancelEditAddress();
  } catch (requestError) {
    const err = toAppError(requestError).message;
    addressSubmitError.value = err;
    toast.show(err, "error");
  } finally {
    showDeleteConfirm.value = false;
    addressToDelete.value = null;
  }
}

async function handleSetDefaultAddress(addr: Address) {
  addressSubmitError.value = "";
  try {
    await makeDefault(addr.id);
    toast.show("Đã đặt làm địa chỉ giao hàng mặc định.", "success");
  } catch (requestError) {
    const err = toAppError(requestError).message;
    addressSubmitError.value = err;
    toast.show(err, "error");
  }
}

onMounted(() => {
  loadAddresses();
});
</script>

<template>
  <AppLayout>
    <div class="account-unified-page space-y-10">
      <!-- Top Title -->
      <header class="space-y-1.5 border-b border-white/10 pb-5">
        <p class="text-xs font-bold uppercase tracking-widest text-emerald-400">Quản Lý Tài Khoản</p>
        <h1 class="text-2xl sm:text-3xl font-black uppercase tracking-tight text-white">
          Hồ Sơ & Sổ Địa Chỉ
        </h1>
        <p class="text-sm text-slate-400">
          Cập nhật thông tin cá nhân và quản lý các địa chỉ nhận hàng trên một trang duy nhất.
        </p>
      </header>

      <!-- Section 1: Profile Information -->
      <section aria-labelledby="profile-heading" class="space-y-4">
        <h2 id="profile-heading" class="text-lg font-black uppercase tracking-tight text-white flex items-center gap-2">
          <span class="flex h-7 w-7 items-center justify-center rounded-lg bg-emerald-500/20 text-emerald-400 text-xs font-black">1</span>
          Thông Tin Cá Nhân
        </h2>

        <div class="rounded-3xl border border-white/10 bg-[#12151e]/85 backdrop-blur-xl p-6 sm:p-8 shadow-2xl">
          <form class="space-y-6" novalidate @submit.prevent="submitProfile">
            <div class="flex items-center gap-4 border-b border-white/10 pb-6">
              <div
                class="flex h-16 w-16 items-center justify-center rounded-2xl border border-emerald-500/30 bg-emerald-500/10 text-2xl font-black text-emerald-400 shadow-[0_0_25px_rgba(16,185,129,0.15)]"
              >
                {{ (fullName || user?.email || "U").charAt(0).toUpperCase() }}
              </div>
              <div>
                <p class="text-base font-bold text-white">{{ fullName || "Chưa cập nhật tên" }}</p>
                <p class="text-xs font-medium text-slate-400">{{ user?.email }}</p>
                <div class="mt-1.5 flex flex-wrap items-center gap-2">
                  <span
                    v-if="user?.roles?.includes('ADMIN')"
                    class="inline-flex items-center gap-1 rounded-md bg-rose-500/20 border border-rose-500/30 px-2 py-0.5 text-[11px] font-extrabold uppercase tracking-wider text-rose-300"
                  >
                    🛡️ Quản trị viên (ADMIN)
                  </span>
                  <span
                    v-else-if="user?.roles?.includes('STAFF')"
                    class="inline-flex items-center gap-1 rounded-md bg-amber-500/20 border border-amber-500/30 px-2 py-0.5 text-[11px] font-extrabold uppercase tracking-wider text-amber-300"
                  >
                    💼 Nhân viên (STAFF)
                  </span>
                  <span
                    v-else
                    class="inline-flex items-center gap-1.5 rounded-md bg-emerald-500/15 border border-emerald-500/30 px-2 py-0.5 text-[10px] font-extrabold uppercase tracking-wider text-emerald-400"
                  >
                    Thành viên Hải Duy Shop
                  </span>

                  <!-- Admin Portal Link if Admin/Staff -->
                  <AppLink
                    v-if="user?.roles?.includes('ADMIN') || user?.roles?.includes('STAFF')"
                    to="/admin"
                    class="inline-flex items-center gap-1 rounded-lg bg-emerald-500 px-3 py-1 text-xs font-black text-slate-950 no-underline shadow-md hover:bg-emerald-400 transition-colors"
                  >
                    Vào Trang Quản Trị &rarr;
                  </AppLink>
                </div>
              </div>
            </div>

            <FormField
              v-slot="field"
              label="Email đăng nhập"
              name="profile-email"
              help="Email gắn liền với tài khoản và không thể thay đổi."
            >
              <BaseInput
                :model-value="user?.email || ''"
                :id="field.id"
                name="profile-email"
                type="email"
                autocomplete="email"
                :aria-describedby="field.describedBy"
                disabled
                class="opacity-75 cursor-not-allowed"
              />
            </FormField>

            <FormField v-slot="field" label="Họ và tên" name="fullName" :error="fullNameError" required>
              <BaseInput
                v-model="fullName"
                :id="field.id"
                name="full_name"
                autocomplete="name"
                placeholder="Nhập họ và tên đầy đủ"
                :invalid="field.invalid"
                :aria-describedby="field.describedBy"
                @blur="blurFullName"
              />
            </FormField>

            <div class="flex justify-end pt-2">
              <BaseButton
                type="submit"
                :loading="profileLoading"
                class="min-h-11 px-6 text-xs sm:text-sm font-black uppercase tracking-wider rounded-xl shadow-[0_8px_20px_rgba(16,185,129,0.3)]"
              >
                Lưu hồ sơ
              </BaseButton>
            </div>
          </form>
        </div>
      </section>

      <!-- Section 2: Addresses Management (Unified on the same page!) -->
      <section id="addresses-section" aria-labelledby="addresses-heading" class="space-y-4 pt-4 border-t border-white/10">
        <h2 id="addresses-heading" class="text-lg font-black uppercase tracking-tight text-white flex items-center gap-2">
          <span class="flex h-7 w-7 items-center justify-center rounded-lg bg-emerald-500/20 text-emerald-400 text-xs font-black">2</span>
          Sổ Địa Chỉ Giao Hàng
        </h2>

        <div class="grid gap-8 lg:grid-cols-[minmax(0,1.15fr)_minmax(20rem,0.85fr)]">
          <!-- Left: Existing Addresses List -->
          <div class="space-y-4">
            <AppAlert v-if="addressesLoadError" variant="error" title="Không thể tải danh sách địa chỉ">
              {{ addressesLoadError }}
            </AppAlert>

            <div v-if="addressesLoading" class="p-8 text-center text-slate-400">
              <svg class="mx-auto h-6 w-6 animate-spin text-emerald-400 mb-2" viewBox="0 0 24 24" fill="none">
                <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4" />
                <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8v8H4z" />
              </svg>
              <span class="text-xs font-semibold">Đang tải địa chỉ…</span>
            </div>

            <div
              v-else-if="addresses.length === 0"
              class="rounded-3xl border border-dashed border-white/15 bg-white/5 p-8 text-center"
            >
              <p class="font-bold text-white">Bạn chưa có địa chỉ nhận hàng nào.</p>
              <p class="mt-1 text-xs text-slate-400">
                Hãy tạo địa chỉ đầu tiên ở biểu mẫu bên cạnh để phục vụ đặt hàng.
              </p>
            </div>

            <div v-else class="space-y-3">
              <div
                v-for="addr in addresses"
                :key="addr.id"
                :class="[
                  'rounded-2xl border p-4 sm:p-5 transition-all backdrop-blur-xl shadow-lg',
                  addr.is_default
                    ? 'border-emerald-500/50 bg-[#121722]/90 shadow-[0_10px_25px_rgba(16,185,129,0.1)]'
                    : 'border-white/10 bg-[#12151e]/85 hover:border-white/20'
                ]"
              >
                <div class="flex flex-wrap items-start justify-between gap-3">
                  <div>
                    <div class="flex items-center gap-2">
                      <h3 class="font-black text-white text-sm sm:text-base">{{ addr.recipient_name }}</h3>
                      <span
                        v-if="addr.is_default"
                        class="rounded-full bg-emerald-500/15 border border-emerald-500/30 px-2 py-0.5 text-[10px] font-bold uppercase text-emerald-400"
                      >
                        Mặc định
                      </span>
                    </div>
                    <p class="text-xs font-semibold text-emerald-400/90 mt-0.5">{{ addr.phone_number }}</p>
                    <address class="mt-1.5 text-xs text-slate-300 not-italic leading-relaxed">
                      {{ addr.street_address }}, {{ addr.ward }}, {{ addr.district }}, {{ addr.province }}
                    </address>
                  </div>

                  <div class="flex items-center gap-2">
                    <BaseButton
                      size="sm"
                      variant="ghost"
                      class="rounded-lg border border-white/15 text-slate-300 hover:text-white text-xs font-bold"
                      @click="beginEditAddress(addr)"
                    >
                      Sửa
                    </BaseButton>
                    <BaseButton
                      size="sm"
                      variant="ghost"
                      class="rounded-lg border border-rose-500/20 bg-rose-500/10 text-rose-400 hover:bg-rose-500/20 text-xs font-bold"
                      @click="promptDeleteAddress(addr)"
                    >
                      Xóa
                    </BaseButton>
                  </div>
                </div>

                <div v-if="!addr.is_default" class="mt-3 pt-2.5 border-t border-white/5">
                  <button
                    type="button"
                    class="text-[11px] font-bold text-slate-400 hover:text-emerald-400 cursor-pointer"
                    :disabled="addressActionLoading"
                    @click="handleSetDefaultAddress(addr)"
                  >
                    + Đặt làm địa chỉ mặc định
                  </button>
                </div>
              </div>
            </div>
          </div>

          <!-- Right: Add / Edit Address Form -->
          <div
            id="address-form-box"
            class="self-start rounded-3xl border border-white/10 bg-[#12151e]/85 backdrop-blur-xl p-5 sm:p-6 shadow-2xl"
          >
            <h3 class="text-base font-black uppercase tracking-tight text-white">
              {{ editingAddressId ? "Cập nhật địa chỉ" : "Thêm địa chỉ nhận hàng" }}
            </h3>

            <form class="mt-4 space-y-3.5" novalidate @submit.prevent="submitAddress">
              <FormField
                v-slot="field"
                label="Họ tên người nhận"
                name="recipientName"
                :error="recipientNameError"
                required
              >
                <BaseInput
                  v-model="recipientName"
                  :id="field.id"
                  name="recipient_name"
                  autocomplete="name"
                  placeholder="Nguyễn Văn A"
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
                  placeholder="0912345678"
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
                label="Địa chỉ chi tiết (Số nhà, đường)"
                name="streetAddress"
                :error="streetAddressError"
                required
              >
                <BaseInput
                  v-model="streetAddress"
                  :id="field.id"
                  name="street_address"
                  autocomplete="street-address"
                  placeholder="Số 18 Phố Duy Tân"
                  :invalid="field.invalid"
                  :aria-describedby="field.describedBy"
                  required
                />
              </FormField>

              <div class="flex items-center justify-end gap-2.5 pt-2">
                <BaseButton
                  v-if="editingAddressId"
                  type="button"
                  variant="ghost"
                  class="rounded-xl border border-white/15 text-slate-300 hover:bg-white/10 text-xs font-bold"
                  @click="cancelEditAddress"
                >
                  Hủy
                </BaseButton>
                <BaseButton
                  type="submit"
                  class="min-h-10 px-5 rounded-xl text-xs font-black uppercase tracking-wider"
                  :loading="addressActionLoading"
                >
                  {{ editingAddressId ? "Lưu thay đổi" : "Thêm địa chỉ" }}
                </BaseButton>
              </div>
            </form>
          </div>
        </div>
      </section>
    </div>

    <!-- Confirm Delete Modal -->
    <AppPopup
      v-model="showDeleteConfirm"
      mode="confirm"
      variant="error"
      title="Xác nhận xóa địa chỉ"
      :message="`Bạn có chắc chắn muốn xóa địa chỉ nhận hàng của '${addressToDelete?.recipient_name}'?`"
      action-text="Xóa vĩnh viễn"
      cancel-text="Giữ lại"
      :loading="addressActionLoading"
      @confirm="handleConfirmedDeleteAddress"
    />
  </AppLayout>
</template>

<style scoped>
.account-unified-page {
  --color-input-bg: #0b0e14;
  --color-border: rgba(255, 255, 255, 0.15);
  --color-text: #ffffff;
  --color-text-muted: #94a3b8;
}
</style>
