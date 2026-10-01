import type { ExchangeStatus } from "./types";

export const exchangeStatusLabels: Record<ExchangeStatus, string> = {
  pending: "Chờ duyệt",
  approved: "Đã duyệt",
  received: "Đã nhận hàng",
  inspected: "Đã kiểm hàng",
  replacement_ready: "Sẵn sàng giao đổi",
  replacement_shipped: "Đang giao hàng đổi",
  completed: "Hoàn tất",
  rejected: "Từ chối",
  cancelled: "Đã hủy",
};

export function exchangeStatusClass(status: ExchangeStatus): string {
  if (status === "completed") return "bg-emerald-500/15 text-emerald-400";
  if (status === "rejected" || status === "cancelled") return "bg-rose-500/15 text-rose-400";
  if (status === "pending") return "bg-amber-500/15 text-amber-400";
  return "bg-sky-500/15 text-sky-400";
}
