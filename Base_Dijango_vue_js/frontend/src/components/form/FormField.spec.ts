import { mount } from "@vue/test-utils";
import { h } from "vue";

import BaseInput from "@/components/base/BaseInput.vue";

import FormField from "./FormField.vue";

describe("FormField", () => {
  it("links label, input, help and error semantics", () => {
    const wrapper = mount(FormField, {
      props: { label: "Email", name: "email", help: "Dùng email công việc", error: "Email sai" },
      slots: {
        default: ({ id, describedBy, invalid }: Record<string, unknown>) =>
          h(BaseInput, {
            modelValue: "",
            id: String(id),
            name: "email",
            invalid: Boolean(invalid),
            "aria-describedby": String(describedBy),
          }),
      },
    });
    const label = wrapper.get("label");
    const input = wrapper.get("input");
    expect(label.attributes("for")).toBe(input.attributes("id"));
    expect(input.attributes("aria-describedby")).toContain("help");
    expect(input.attributes("aria-describedby")).toContain("error");
    expect(wrapper.get('[role="alert"]').text()).toContain("Email sai");
  });
});
