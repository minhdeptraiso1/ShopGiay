import { mount } from "@vue/test-utils";
import { createMemoryHistory, createRouter } from "vue-router";

import RegisterPage from "./RegisterPage.vue";

describe("RegisterPage", () => {
  it("renders accessible registration fields with browser autocomplete", async () => {
    const router = createRouter({
      history: createMemoryHistory(),
      routes: [
        { path: "/register", component: RegisterPage },
        { path: "/login", name: "login", component: { template: "<div />" } },
      ],
    });
    await router.push("/register");
    await router.isReady();
    const wrapper = mount(RegisterPage, { global: { plugins: [router] } });

    expect(wrapper.get('input[name="full_name"]').attributes("autocomplete")).toBe("name");
    expect(wrapper.get('input[name="email"]').attributes("autocomplete")).toBe("email");
    expect(wrapper.get('input[name="password"]').attributes("autocomplete")).toBe("new-password");
    expect(wrapper.get('input[name="password_confirm"]').attributes("autocomplete")).toBe(
      "new-password",
    );
    expect(
      wrapper.findAll("input").every((input) => input.attributes("required") !== undefined),
    ).toBe(true);
  });
});
