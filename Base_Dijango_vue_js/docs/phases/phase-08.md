# Phase 8 - Báo cáo và hoàn thiện vận hành

**Trạng thái:** In progress
**Nhánh đề xuất:** `phase/08-reporting-operations`
**Điều kiện bắt đầu:** Phase 7 Done; thống nhất định nghĩa KPI và timezone báo cáo.

## Sprint 1 - Dashboard và doanh thu

- Định nghĩa doanh thu theo payment captured/completed và cancellation theo thời điểm rõ ràng.
- API aggregate theo date range/timezone; permission riêng cho từng nhóm báo cáo.
- FE dashboard có filter, loading/empty/error và so sánh kỳ; không tính tiền ở client.
- Index/query plan được kiểm tra; aggregate lớn dùng bảng tổng hợp/job khi có bằng chứng cần thiết.

## Sprint 2 - Báo cáo nghiệp vụ

- Bán chạy theo quantity và net revenue.
- Tồn thấp, ageing và stock movement.
- Tỷ lệ hủy theo reason/status, tỷ lệ đổi hàng và thời gian xử lý đổi.
- Recommendation impressions/CTR/cart/purchase/coverage theo strategy/placement.

## Sprint 3 - Staff, audit, giá vốn và export

- Hoàn thiện tạo/deactivate STAFF, gán role/permission và ngăn tự nâng quyền.
- Audit log append-only cho role, product, stock, order, voucher, exchange và settings quan trọng.
- Phiếu nhập kho thủ công/CSV, giá vốn bình quân gia quyền và snapshot giá vốn lúc bán.
- Lợi nhuận = doanh thu thuần - giá vốn; chưa trừ phí giao hàng/VNPay.
- Một file Excel `.xlsx` tổng hợp nhiều sheet theo filter và permission.

## Sprint 4 - Danh sách lớn và realtime

- Server-side pagination mặc định 20 dòng/trang cho toàn bộ màn quản trị.
- Tìm kiếm, trạng thái, khoảng ngày và “đơn hôm nay” ở các màn phù hợp.
- Django Channels + Redis cập nhật đơn, đổi hàng, kho và notification không cần F5.
- Notification lưu DB, có đã đọc/chưa đọc cho khách hàng và nhân viên.

## API/màn hình dự kiến

`/api/v1/admin/dashboard/`, `/reports/sales/`, `/reports/inventory/`, `/reports/returns/`,
`/reports/recommendations/`, `/admin/staff/`, `/admin/audit-logs/`; dashboard cards/charts, report tables và
export controls.

## Tiêu chí nghiệm thu

Số dashboard đối soát được với order/payment/exchange mẫu; timezone và date boundary có test; query không
N+1; export an toàn; chỉ đúng permission xem dữ liệu; mọi thao tác quản trị quan trọng có audit.

## Cần chốt trước khi duyệt

Định nghĩa doanh thu chính thức, timezone, kỳ báo cáo, format export và thời hạn giữ audit log.

## Kết quả triển khai

- Dashboard đã bỏ mock, dùng aggregate backend theo `Asia/Ho_Chi_Minh`; STAFF thấy hàng đợi/tồn thấp,
  ADMIN thấy thêm doanh thu, đơn paid, AOV và biểu đồ ngày.
- Có báo cáo doanh thu/bán chạy/hủy, tồn thấp/ageing/movement, đổi hàng và recommendation; xuất một file
  Excel nhiều sheet. Dashboard hiển thị doanh thu thuần, giá vốn và lợi nhuận.
- ADMIN quản lý tạo, khóa/kích hoạt STAFF; payload không thể tự gán ADMIN. Audit append-only ghi role,
  product/variant, stock movement, order, voucher/banner và exchange; chỉ ADMIN đọc được.
- Audit giữ mặc định 730 ngày qua `AUDIT_LOG_RETENTION_DAYS`; command `purge_audit_logs --dry-run` hỗ trợ
  kiểm tra trước khi dọn theo lịch vận hành.
- Thêm phiếu nhập kho thủ công/CSV, cost snapshot, notification DB, WebSocket ticket một lần và phân trang
  server-side 20 dòng/trang cho các màn quản trị.
- Migration đã tạo nhưng chưa áp dụng vì PostgreSQL local đang từ chối mật khẩu. Ruff, Django check,
  migration drift, OpenAPI, frontend typecheck/lint/format, 27 frontend test và build đều pass. Backend
  chạy dự phòng trên SQLite đạt 95 test, bỏ qua 1 test khóa dòng riêng PostgreSQL; vẫn cần chạy lại toàn
  bộ suite trên PostgreSQL sau khi sửa kết nối DB.

