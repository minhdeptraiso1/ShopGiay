import { flushPromises, mount } from "@vue/test-utils";
import { beforeEach, describe, expect, it, vi } from "vitest";

import AdminHomePage from "./AdminHomePage.vue";

const authState = vi.hoisted(() => ({
  user: {
    value: {
      id: 2,
      email: "staff@example.com",
      full_name: "Nhân viên Local",
      roles: ["STAFF"],
    },
  },
}));

vi.mock("@/modules/auth/composables/useAuth", () => ({
  useAuth: () => ({ user: authState.user }),
}));

vi.mock("@/modules/admin/api", () => ({
  verifyAdminAccessRequest: vi.fn().mockResolvedValue("ok"),
}));

const global = {
  stubs: {
    AdminLayout: { template: "<main><slot /></main>" },
    AppLink: { template: "<a><slot /></a>" },
  },
};

describe("AdminHomePage", () => {
  beforeEach(() => {
    authState.user.value.roles = ["STAFF"];
  });

  it("shows the operations workspace for staff", async () => {
    const wrapper = mount(AdminHomePage, { global });
    await flushPromises();

    expect(wrapper.text()).toContain("Bảng công việc trong ca");
    expect(wrapper.text()).toContain("Chờ xác nhận");
    expect(wrapper.text()).not.toContain("Doanh thu hôm nay");
    expect(wrapper.text()).not.toContain("Thêm sản phẩm");
  });

  it("shows business metrics and catalog action for admin", async () => {
    authState.user.value.roles = ["ADMIN"];
    const wrapper = mount(AdminHomePage, { global });
    await flushPromises();

    expect(wrapper.text()).toContain("Tổng quan kinh doanh");
    expect(wrapper.text()).toContain("Doanh thu hôm nay");
    expect(wrapper.text()).toContain("Thêm sản phẩm");
  });
});
