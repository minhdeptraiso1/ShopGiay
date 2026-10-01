import { describe, expect, it } from "vitest";

import { canPayOrderWithVnpay } from "./payment";

describe("canPayOrderWithVnpay", () => {
  it("allows an unpaid active VNPay order", () => {
    expect(
      canPayOrderWithVnpay({
        payment_method: "vnpay",
        payment_status: "pending",
        status: "pending_confirmation",
      }),
    ).toBe(true);
  });

  it("does not offer VNPay for a COD order", () => {
    expect(
      canPayOrderWithVnpay({
        payment_method: "cod",
        payment_status: "pending",
        status: "pending_confirmation",
      }),
    ).toBe(false);
  });

  it("does not offer payment for paid or cancelled orders", () => {
    expect(
      canPayOrderWithVnpay({
        payment_method: "vnpay",
        payment_status: "paid",
        status: "confirmed",
      }),
    ).toBe(false);
    expect(
      canPayOrderWithVnpay({
        payment_method: "vnpay",
        payment_status: "pending",
        status: "cancelled",
      }),
    ).toBe(false);
  });
});
