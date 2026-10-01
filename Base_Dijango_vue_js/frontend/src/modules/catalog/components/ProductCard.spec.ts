import { mount } from "@vue/test-utils";
import { createMemoryHistory, createRouter } from "vue-router";
import { createPinia } from "pinia";
import { describe, expect, it } from "vitest";

import ProductCard from "./ProductCard.vue";
import type { ProductListItem } from "../types";

const product: ProductListItem = {
  id: 1,
  name: "Speed Pro",
  slug: "speed-pro",
  category: null,
  brand: null,
      product_type: "footwear",
  primary_image: null,
  min_price: "2650000",
  max_price: "2650000",
  currency: "VND",
  is_available: true,
  published_at: "2026-09-18T00:00:00Z",
};

describe("ProductCard", () => {
  it("renders API product data and links to its detail page", async () => {
    const router = createRouter({
      history: createMemoryHistory(),
      routes: [
        { path: "/", name: "home", component: { template: "<div />" } },
        { path: "/products/:slug", name: "product-detail", component: { template: "<div />" } },
      ],
    });
    await router.push("/");
    await router.isReady();

    const wrapper = mount(ProductCard, {
      props: { product },
      global: { plugins: [createPinia(), router] },
    });

    expect(wrapper.text()).toContain("Speed Pro");
    expect(wrapper.text()).toContain("2.650.000");
    expect(wrapper.text()).toContain("Còn hàng");
    expect(wrapper.find("a").attributes("href")).toBe("/products/speed-pro");
  });
});
