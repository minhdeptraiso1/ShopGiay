import type { Router } from "vue-router";

import { bootstrapAuth } from "@/modules/auth/composables/useAuth";
import { useAuthStore } from "@/modules/auth/stores/auth";
import type { BusinessRole } from "@/modules/auth/types";

export function installRouterGuards(router: Router) {
  router.beforeEach(async (to) => {
    const auth = useAuthStore();
    await bootstrapAuth();

    if (to.meta.requiresAuth && !auth.isAuthenticated) {
      return { name: "login", query: { redirect: to.fullPath } };
    }
    const requiredRoles = to.meta.requiredRoles as BusinessRole[] | undefined;
    if (requiredRoles?.length && !requiredRoles.some((role) => auth.hasRole(role))) {
      return { name: "forbidden" };
    }
    if (to.meta.guestOnly && auth.isAuthenticated) {
      if (auth.hasRole("ADMIN") || auth.hasRole("STAFF")) {
        return router.hasRoute("admin-home") ? { name: "admin-home" } : { name: "home" };
      }
      return { name: "home" };
    }
    return true;
  });
}
