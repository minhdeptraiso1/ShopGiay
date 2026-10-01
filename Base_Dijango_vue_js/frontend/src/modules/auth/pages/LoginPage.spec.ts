import { createPinia, setActivePinia } from "pinia";
import { mount } from "@vue/test-utils";
import { ref } from "vue";
import { createMemoryHistory, createRouter } from "vue-router";
import { vi } from "vitest";

import LoginPage from "./LoginPage.vue";

const login = vi.fn<() => Promise<void>>().mockResolvedValue(undefined);

vi.mock("../composables/useAuth", () => ({
  useAuth: () => ({
    login,
    logout: vi.fn(),
    loginLoading: ref(false),
    logoutLoading: ref(false),
  }),
}));

describe("LoginPage", () => {
  it("renders accessible, browser-assisted login fields", async () => {
    const pinia = createPinia();
    setActivePinia(pinia);
    const router = createRouter({
      history: createMemoryHistory(),
      routes: [
        { path: "/login", component: LoginPage },
        { path: "/register", component: { template: "<div />" } },
        { path: "/forgot-password", component: { template: "<div />" } },
      ],
    });
    await router.push("/login");
    await router.isReady();

    const wrapper = mount(LoginPage, { global: { plugins: [pinia, router] } });
    expect(wrapper.get('input[name="email"]').attributes("autocomplete")).toBe("email");
    expect(wrapper.get('input[name="password"]').attributes("autocomplete")).toBe(
      "current-password",
    );

    expect(wrapper.get('input[name="email"]').attributes("required")).toBeDefined();
    expect(wrapper.get('input[name="password"]').attributes("required")).toBeDefined();
    expect(login).not.toHaveBeenCalled();
  });
});
