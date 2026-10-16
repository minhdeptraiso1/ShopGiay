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
const fetchDashboardMock = vi.hoisted(() => vi.fn());

vi.mock("@/modules/auth/composables/useAuth", () => ({
  useAuth: () => ({ user: authState.user }),
}));

vi.mock("@/modules/operations/api", () => ({
  fetchDashboard: fetchDashboardMock,
}));

const dashboardResponse = {
  range: { start: "2026-09-24", end: "2026-10-01", timezone: "Asia/Ho_Chi_Minh" },
  queue: { pending_confirmation: 7, preparing: 2, shipped: 3, completed: 4 },
  low_stock_count: 5,
  recent_activity: [],
  revenue_series: [],
  finance: {
    revenue: "18600000",
    revenue_change_percent: "12.4",
    paid_order_count: 24,
    average_order_value: "1420000",
    net_revenue: "18000000",
    cost_of_goods_sold: "11000000",
    profit: "7000000",
  },
};

const global = {
  stubs: {
    AdminLayout: { template: "<main><slot /></main>" },
    AppLink: { template: "<a><slot /></a>" },
  },
};

describe("AdminHomePage", () => {
  beforeEach(() => {
    authState.user.value.roles = ["STAFF"];
    fetchDashboardMock.mockResolvedValue(dashboardResponse);
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
    expect(wrapper.text()).toContain("Doanh thu thuần");
    expect(wrapper.text()).toContain("Lợi nhuận");
    expect(wrapper.text()).toContain("Xu hướng doanh thu thực tế");
  });
});
