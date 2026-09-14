# Phase 8 - Báo cáo và hoàn thiện vận hành

**Trạng thái:** Planned  
**Nhánh đề xuất:** `phase/08-reporting-operations`  
**Điều kiện bắt đầu:** Phase 7 Done; thống nhất định nghĩa KPI và timezone báo cáo.

## Sprint 1 - Dashboard và doanh thu

- Định nghĩa doanh thu theo payment captured/completed, trừ cancellation/refund theo thời điểm rõ ràng.
- API aggregate theo date range/timezone; permission riêng cho từng nhóm báo cáo.
- FE dashboard có filter, loading/empty/error và so sánh kỳ; không tính tiền ở client.
- Index/query plan được kiểm tra; aggregate lớn dùng bảng tổng hợp/job khi có bằng chứng cần thiết.

## Sprint 2 - Báo cáo nghiệp vụ

- Bán chạy theo quantity và net revenue.
- Tồn thấp, ageing và stock movement.
- Tỷ lệ hủy theo reason/status, return/refund amount và turnaround time.
- Recommendation impressions/CTR/cart/purchase/coverage theo strategy/placement.

## Sprint 3 - Staff, audit và export

- Hoàn thiện tạo/deactivate STAFF, gán role/permission và ngăn tự nâng quyền.
- Audit log append-only cho role, product, stock, order, voucher, return, refund và settings quan trọng.
- Export CSV theo filter và permission; spreadsheet formula injection được neutralize.

## API/màn hình dự kiến

`/api/v1/admin/dashboard/`, `/reports/sales/`, `/reports/inventory/`, `/reports/returns/`,
`/reports/recommendations/`, `/admin/staff/`, `/admin/audit-logs/`; dashboard cards/charts, report tables và
export controls.

## Tiêu chí nghiệm thu

Số dashboard đối soát được với order/payment/refund mẫu; timezone và date boundary có test; query không
N+1; export an toàn; chỉ đúng permission xem dữ liệu; mọi thao tác quản trị quan trọng có audit.

## Cần chốt trước khi duyệt

Định nghĩa doanh thu chính thức, timezone, kỳ báo cáo, format export và thời hạn giữ audit log.

