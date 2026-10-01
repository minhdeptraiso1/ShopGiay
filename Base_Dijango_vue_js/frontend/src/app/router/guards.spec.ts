import { createPinia, setActivePinia } from "pinia";
import { createMemoryHistory, createRouter } from "vue-router";
import { vi } from "vitest";

import { useAuthStore } from "@/modules/auth/stores/auth";

import { installRouterGuards } from "./guards";

vi.mock("@/modules/auth/composables/useAuth", () => ({
  bootstrapAuth: vi.fn().mockResolvedValue(undefined),
}));

function makeRouter() {
  const router = createRouter({
    history: createMemoryHistory(),
    routes: [
      { path: "/", name: "home", component: { template: "<div />" } },
      { path: "/login", name: "login", component: { template: "<div />" } },
      { path: "/403", name: "forbidden", component: { template: "<div />" } },
      {
        path: "/admin",
        name: "admin",
        component: { template: "<div />" },
        meta: { requiresAuth: true, requiredRoles: ["STAFF", "ADMIN"] },
      },
    ],
  });
  installRouterGuards(router);
  return router;
}

describe("role route guards", () => {
  it("redirects a guest to login and preserves the destination", async () => {
    setActivePinia(createPinia());
    const router = makeRouter();
    await router.push("/admin");
    expect(router.currentRoute.value.name).toBe("login");
    expect(router.currentRoute.value.query.redirect).toBe("/admin");
  });

  it("blocks a customer but allows a staff account", async () => {
    setActivePinia(createPinia());
    const auth = useAuthStore();
    const baseUser = {
      id: 1,
      email: "user@example.com",
      full_name: "User",
      is_active: true,
      date_joined: "2026-09-14T00:00:00Z",
      permissions: [],
    };
    auth.setSession({ ...baseUser, roles: ["CUSTOMER"] }, "token");
    const router = makeRouter();
    await router.push("/admin");
    expect(router.currentRoute.value.name).toBe("forbidden");

    auth.setSession({ ...baseUser, roles: ["STAFF"] }, "token");
    await router.push("/admin");
    expect(router.currentRoute.value.name).toBe("admin");
  });
});
