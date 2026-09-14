import { mount } from "@vue/test-utils";

import BaseButton from "./BaseButton.vue";

describe("BaseButton", () => {
  it("defaults to button and blocks interaction while loading", async () => {
    const wrapper = mount(BaseButton, { props: { loading: true }, slots: { default: "Lưu" } });
    const button = wrapper.get("button");
    expect(button.attributes("type")).toBe("button");
    expect(button.attributes("disabled")).toBeDefined();
    expect(button.attributes("aria-busy")).toBe("true");
    await button.trigger("click");
    expect(wrapper.emitted("click")).toBeUndefined();
  });
});
