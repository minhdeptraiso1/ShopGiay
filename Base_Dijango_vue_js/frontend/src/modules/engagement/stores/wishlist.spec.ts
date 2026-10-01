import { createPinia, setActivePinia } from "pinia";
import { beforeEach, describe, expect, it, vi } from "vitest";

import { fetchWishlist, toggleWishlist } from "../api";
import type { ProductListItem } from "../../catalog/types";
import { useWishlistStore } from "./wishlist";

vi.mock("../api", () => ({
  fetchWishlist: vi.fn(),
  removeWishlist: vi.fn(),
  toggleWishlist: vi.fn(),
}));

const product: ProductListItem = {
  id: 7,
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

describe("wishlist store", () => {
  beforeEach(() => {
    setActivePinia(createPinia());
    vi.clearAllMocks();
  });

  it("loads items and refreshes after a toggle", async () => {
    vi.mocked(fetchWishlist)
      .mockResolvedValueOnce([])
      .mockResolvedValueOnce([{ id: 3, product, created_at: "2026-09-29T00:00:00Z" }]);
    vi.mocked(toggleWishlist).mockResolvedValue(true);

    const wishlist = useWishlistStore();
    await wishlist.load();
    expect(wishlist.count).toBe(0);

    await wishlist.toggle(product.id);
    expect(wishlist.has(product.id)).toBe(true);
    expect(wishlist.count).toBe(1);
  });
});
