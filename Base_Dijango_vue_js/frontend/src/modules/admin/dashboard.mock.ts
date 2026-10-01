export interface DashboardMetric {
  label: string;
  value: string;
  change: string;
  trend: "up" | "down" | "neutral";
  helper: string;
}

export interface QueueSummary {
  label: string;
  count: number;
  helper: string;
  tone: "amber" | "sky" | "violet" | "emerald";
}

export const ADMIN_METRICS: DashboardMetric[] = [
  {
    label: "Doanh thu hôm nay",
    value: "18,6 triệu",
    change: "+12,4%",
    trend: "up",
    helper: "so với hôm qua",
  },
  { label: "Đơn hàng mới", value: "24", change: "+5 đơn", trend: "up", helper: "trong 24 giờ" },
  {
    label: "Giá trị đơn TB",
    value: "1,42 triệu",
    change: "+3,1%",
    trend: "up",
    helper: "7 ngày gần nhất",
  },
  {
    label: "SKU sắp hết",
    value: "8",
    change: "Cần xử lý",
    trend: "down",
    helper: "dưới ngưỡng an toàn",
  },
];

export const STAFF_METRICS: DashboardMetric[] = [
  { label: "Chờ xác nhận", value: "7", change: "Ưu tiên", trend: "down", helper: "đơn cần xử lý" },
  {
    label: "Đang chuẩn bị",
    value: "11",
    change: "+3 đơn",
    trend: "neutral",
    helper: "trong ca hiện tại",
  },
  {
    label: "Sẵn sàng giao",
    value: "9",
    change: "Đúng tiến độ",
    trend: "up",
    helper: "đã đóng gói",
  },
  {
    label: "SKU sắp hết",
    value: "8",
    change: "Cần kiểm tra",
    trend: "down",
    helper: "dưới ngưỡng an toàn",
  },
];

export const ORDER_QUEUE: QueueSummary[] = [
  { label: "Chờ xác nhận", count: 7, helper: "Đơn mới cần kiểm tra thanh toán", tone: "amber" },
  { label: "Đang chuẩn bị", count: 11, helper: "Đang lấy hàng và đóng gói", tone: "sky" },
  { label: "Đang giao", count: 18, helper: "Đã bàn giao cho đơn vị vận chuyển", tone: "violet" },
  { label: "Hoàn thành hôm nay", count: 32, helper: "Đơn đã giao thành công", tone: "emerald" },
];

export const WEEKLY_REVENUE = [
  { label: "T2", value: 42 },
  { label: "T3", value: 58 },
  { label: "T4", value: 46 },
  { label: "T5", value: 71 },
  { label: "T6", value: 64 },
  { label: "T7", value: 88 },
  { label: "CN", value: 76 },
];

export const RECENT_ACTIVITY = [
  { time: "10:42", title: "Đơn #HD-1048 đã chuyển sang chuẩn bị", actor: "Nhân viên kho" },
  { time: "10:18", title: "Nhập thêm 12 đôi Speed Pro size 41", actor: "Admin Local" },
  { time: "09:55", title: "Đơn #HD-1046 đã xác nhận thanh toán", actor: "Hệ thống VNPay" },
  { time: "09:31", title: "Cập nhật ảnh đại diện Matrix Knit Racer", actor: "Admin Local" },
];
