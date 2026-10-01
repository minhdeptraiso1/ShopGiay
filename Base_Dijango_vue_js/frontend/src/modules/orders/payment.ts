import type { Order } from "@/modules/cart/types";

type PayableOrder = Pick<Order, "payment_method" | "payment_status" | "status">;

export function canPayOrderWithVnpay(order: PayableOrder | null): boolean {
  return (
    order?.payment_method === "vnpay" &&
    order.payment_status !== "paid" &&
    order.status !== "cancelled"
  );
}
