import { describe, expect, it } from "vitest";

import { toSlug } from "./slug";

describe("toSlug", () => {
  it("converts Vietnamese names to URL-safe slugs", () => {
    expect(toSlug("Giày Adidas Chính Hãng")).toBe("giay-adidas-chinh-hang");
  });

  it("normalizes punctuation, whitespace and repeated dashes", () => {
    expect(toSlug("  Air Max -- 360!  ")).toBe("air-max-360");
  });
});
