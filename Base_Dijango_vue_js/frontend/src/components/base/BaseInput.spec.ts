import { mount } from "@vue/test-utils";

import BaseInput from "./BaseInput.vue";

describe("BaseInput", () => {
  it("forwards accessible attributes and updates v-model without trimming", async () => {
    const wrapper = mount(BaseInput, {
      props: {
        modelValue: "",
        id: "password",
        name: "password",
        type: "password" as const,
        invalid: true,
        "aria-describedby": "password-error",
        "onUpdate:modelValue": (value: string) => wrapper.setProps({ modelValue: value }),
      },
    });
    const input = wrapper.get("input");
    await input.setValue("  secret  ");
    expect(wrapper.props("modelValue")).toBe("  secret  ");
    expect(input.attributes("aria-invalid")).toBe("true");
    expect(input.attributes("aria-describedby")).toBe("password-error");

    const toggle = wrapper.get("button");
    expect(toggle.attributes("type")).toBe("button");
    expect(toggle.attributes("aria-label")).toBe("Hiện mật khẩu");
    await toggle.trigger("click");
    expect(wrapper.get("input").attributes("type")).toBe("text");
  });
});
