import { createPinia, setActivePinia } from "pinia";
import { mount } from "@vue/test-utils";
import { ref } from "vue";
import { createMemoryHistory, createRouter } from "vue-router";
import { vi } from "vitest";

import { useAuthStore } from "@/modules/auth/stores/auth";

import ProfilePage from "./ProfilePage.vue";

vi.mock("@/modules/auth/composables/useAuth", () => ({
  useAuth: () => ({
    user: ref(null),
    logout: vi.fn(),
    logoutLoading: ref(false),
    logoutError: ref(""),
  }),
}));

describe("ProfilePage", () => {
  it("shows email as read-only and only exposes full_name for editing", async () => {
    const pinia = createPinia();
    setActivePinia(pinia);
    useAuthStore().setSession(
      {
        id: 1,
        email: "demo@example.com",
        full_name: "Demo User",
        is_active: true,
        date_joined: "2026-09-12T12:00:00Z",
        roles: ["CUSTOMER"],
        permissions: [],
      },
      "memory-access-token",
    );
    const router = createRouter({
      history: createMemoryHistory(),
      routes: [
        { path: "/", component: { template: "<div />" } },
        { path: "/profile", component: ProfilePage },
        { path: "/profile/addresses", component: { template: "<div />" } },
      ],
    });
    await router.push("/profile");
    await router.isReady();

    const wrapper = mount(ProfilePage, { global: { plugins: [pinia, router] } });
    expect(wrapper.get('input[name="profile-email"]').attributes("disabled")).toBeDefined();
    expect((wrapper.get('input[name="profile-email"]').element as HTMLInputElement).value).toBe(
      "demo@example.com",
    );
    expect((wrapper.get('input[name="full_name"]').element as HTMLInputElement).value).toBe(
      "Demo User",
    );
  });
});
