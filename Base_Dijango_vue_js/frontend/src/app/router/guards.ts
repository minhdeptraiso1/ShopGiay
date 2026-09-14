import type { Router } from "vue-router";

import { bootstrapAuth } from "@/modules/auth/composables/useAuth";
import { useAuthStore } from "@/modules/auth/stores/auth";

export function installRouterGuards(router: Router) {
  router.beforeEach(async (to) => {
    const auth = useAuthStore();
    await bootstrapAuth();

    if (to.meta.requiresAuth && !auth.isAuthenticated) {
      return { name: "login", query: { redirect: to.fullPath } };
    }
    if (to.meta.guestOnly && auth.isAuthenticated) return { name: "home" };
    return true;
  });
}
