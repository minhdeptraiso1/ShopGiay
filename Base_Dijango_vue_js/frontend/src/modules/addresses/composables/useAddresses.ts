import { ref } from "vue";

import { useToastStore } from "@/app/stores/toast";
import { toAppError } from "@/lib/http/errors";

import {
  createAddressRequest,
  deleteAddressRequest,
  listAddressesRequest,
  setDefaultAddressRequest,
  updateAddressRequest,
} from "../api";
import type { Address, AddressPayload } from "../types";

export function useAddresses() {
  const toast = useToastStore();
  const addresses = ref<Address[]>([]);
  const loading = ref(false);
  const actionLoading = ref(false);
  const error = ref("");

  async function loadAddresses() {
    loading.value = true;
    error.value = "";
    try {
      addresses.value = await listAddressesRequest();
    } catch (requestError) {
      error.value = toAppError(requestError).message;
    } finally {
      loading.value = false;
    }
  }

  async function saveAddress(payload: AddressPayload, id?: number) {
    actionLoading.value = true;
    try {
      if (id) await updateAddressRequest(id, payload);
      else await createAddressRequest(payload);
      await loadAddresses();
      toast.show(id ? "Đã cập nhật địa chỉ." : "Đã thêm địa chỉ.", "success");
    } finally {
      actionLoading.value = false;
    }
  }

  async function removeAddress(id: number) {
    actionLoading.value = true;
    try {
      await deleteAddressRequest(id);
      await loadAddresses();
      toast.show("Đã xóa địa chỉ.", "success");
    } finally {
      actionLoading.value = false;
    }
  }

  async function makeDefault(id: number) {
    actionLoading.value = true;
    try {
      await setDefaultAddressRequest(id);
      await loadAddresses();
      toast.show("Đã đặt làm địa chỉ mặc định.", "success");
    } finally {
      actionLoading.value = false;
    }
  }

  return {
    addresses,
    loading,
    actionLoading,
    error,
    loadAddresses,
    saveAddress,
    removeAddress,
    makeDefault,
  };
}
