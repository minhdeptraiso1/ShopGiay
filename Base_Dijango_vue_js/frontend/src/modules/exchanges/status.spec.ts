import { describe, expect, it } from "vitest";

import { exchangeStatusClass, exchangeStatusLabels } from "./status";

describe("exchange status presentation", () => {
  it("provides a Vietnamese label for every workflow status", () => {
    expect(Object.keys(exchangeStatusLabels)).toHaveLength(9);
    expect(exchangeStatusLabels.replacement_ready).toBe("Sẵn sàng giao đổi");
    expect(exchangeStatusLabels.replacement_shipped).toBe("Đang giao hàng đổi");
  });

  it("uses distinct semantic colors", () => {
    expect(exchangeStatusClass("completed")).toContain("emerald");
    expect(exchangeStatusClass("pending")).toContain("amber");
    expect(exchangeStatusClass("rejected")).toContain("rose");
    expect(exchangeStatusClass("approved")).toContain("sky");
  });
});
