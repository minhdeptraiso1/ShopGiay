import { ref } from "vue";

import { useToastStore } from "@/app/stores/toast";
import { toAppError } from "@/lib/http/errors";
import { useAuthStore } from "@/modules/auth/stores/auth";

import { updateProfileRequest } from "../api";

export function useProfile() {
  const auth = useAuthStore();
  const toast = useToastStore();
  const loading = ref(false);
  const error = ref("");

  async function updateProfile(fullName: string) {
    loading.value = true;
    error.value = "";
    try {
      const user = await updateProfileRequest(fullName);
      if (!auth.accessToken) throw new Error("Missing access token after profile update");
      auth.setSession(user, auth.accessToken);
      toast.show("Đã cập nhật hồ sơ.", "success");
    } catch (requestError) {
      error.value = toAppError(requestError).message;
      throw requestError;
    } finally {
      loading.value = false;
    }
  }

  return { loading, error, updateProfile };
}
