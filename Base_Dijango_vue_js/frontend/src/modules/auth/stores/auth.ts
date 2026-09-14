import { defineStore } from "pinia";
import { computed, ref } from "vue";

import type { User } from "../types";

const LOGOUT_PENDING_KEY = "django-base.logout-pending";

export const useAuthStore = defineStore("auth", () => {
  const user = ref<User | null>(null);
  const accessToken = ref<string | null>(null);
  const bootstrapState = ref<"idle" | "loading" | "ready">("idle");
  const bootstrapError = ref("");
  const generation = ref(0);
  const logoutPending = ref(localStorage.getItem(LOGOUT_PENDING_KEY) === "1");
  const logoutError = ref("");

  const isAuthenticated = computed(() => Boolean(user.value && accessToken.value));

  function setAccessToken(token: string | null) {
    accessToken.value = token;
  }

  function setSession(nextUser: User, token: string) {
    user.value = nextUser;
    accessToken.value = token;
    logoutPending.value = false;
    logoutError.value = "";
    localStorage.removeItem(LOGOUT_PENDING_KEY);
  }

  function clearSession() {
    generation.value += 1;
    user.value = null;
    accessToken.value = null;
  }

  function markLogoutPending(value: boolean) {
    logoutPending.value = value;
    if (value) localStorage.setItem(LOGOUT_PENDING_KEY, "1");
    else localStorage.removeItem(LOGOUT_PENDING_KEY);
  }

  return {
    user,
    accessToken,
    bootstrapState,
    bootstrapError,
    generation,
    logoutPending,
    logoutError,
    isAuthenticated,
    setAccessToken,
    setSession,
    clearSession,
    markLogoutPending,
  };
});
