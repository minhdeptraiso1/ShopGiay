# Phase 5 - Khuyến mãi, yêu thích và đánh giá

**Trạng thái:** Awaiting acceptance
**Nhánh đề xuất:** `phase/05-engagement`  
**Điều kiện bắt đầu:** Phase 4 Done; chốt chính sách voucher và moderation.

> **Deferred từ Phase 4:** cấu hình public HTTPS IPN và kiểm thử VNPay sandbox end-to-end chưa hoàn tất.
> Công việc này không thuộc scope triển khai Phase 5 nhưng phải quay lại xử lý trước release; xem
> [phase-04.md](phase-04.md#note-công-việc-vnpay-hoãn-lại).

## Sprint 1 - Voucher

- DB: Voucher, rule/eligibility, usage reservation/redemption và per-order allocation.
- API admin CRUD; customer validate/apply trong quote và order.
- Backend kiểm tra active window, minimum spend, product/category scope, global/per-user limit.
- Khóa/counter atomic để nhiều checkout không vượt giới hạn.
- Phân bổ giảm giá theo order line bằng largest remainder để lưu đúng net paid của từng sản phẩm.

## Sprint 2 - Wishlist

- DB unique user+product; API list/toggle/remove có ownership.
- FE nút yêu thích ở list/detail và trang wishlist.
- Ghi event wishlist từ backend sau khi mutation thành công; không tin event giả từ client.

## Sprint 3 - Review và moderation

- Chỉ CUSTOMER có order line đủ điều kiện mới được đánh giá; một review/order line theo policy.
- Review có rating, nội dung, trạng thái moderation và audit action.
- Public chỉ thấy review approved; STAFF chỉ moderate khi có permission.
- Xử lý sản phẩm đã ẩn và user bị deactivate mà không phá lịch sử.

## Sprint 4 - Banner/content

- Banner/content block có lịch hiển thị, vị trí và trạng thái.
- Admin editor tối thiểu; storefront fallback khi ảnh hoặc nội dung thiếu.

## API/bảng chính

`/vouchers/validate/`, `/admin/vouchers/`, `/wishlist/`, `/products/{id}/reviews/`, `/admin/reviews/`,
`/banners/`; bảng voucher/usage/allocation, wishlist, review và banner.

## Tiêu chí nghiệm thu

Voucher được tính lại lúc đặt hàng và không oversubscribe; wishlist ownership đúng; review bắt buộc đã mua
và có moderation; banner chỉ hiện đúng lịch; event recommendation liên quan được ghi có nguồn xác thực.

## Kết quả triển khai

- Backend thêm module `engagement` với migration cho voucher/usage/allocation, wishlist, review và banner.
- Voucher được tính lại trong quote và transaction tạo order; usage được reserve/redeem/release theo COD,
  VNPay và hủy đơn, đồng thời phân bổ discount theo từng order line.
- Storefront có wishlist, nút yêu thích ở danh sách/chi tiết, đánh giá verified-purchase và banner động.
- Checkout hỗ trợ nhập/bỏ voucher và luôn gửi lại mã cho backend khi tạo đơn.
- STAFF/ADMIN dùng `/admin/engagement` để moderation; chỉ ADMIN thấy và thao tác voucher/banner.
- Command `seed_engagement` tạo idempotent mã `WELCOME10` và banner demo khi `DEBUG=True`.
- Toàn bộ backend: 75 test pass trực tiếp trên PostgreSQL; frontend: typecheck, 25 Vitest test và
  production build pass. OpenAPI validation, Django check, migration drift và Ruff pass.
- Migration Phase 5 đã áp dụng trên PostgreSQL local và seed `WELCOME10`/banner demo đã chạy thành công.

## Giới hạn đã biết

- Form phạm vi voucher tải trang sản phẩm đầu tiên; catalog lớn cần bổ sung ô tìm kiếm/pagination ở Phase 6.
- Banner hiện dùng URL ảnh thay vì object storage/upload media.
- VNPay sandbox E2E vẫn được hoãn theo note Phase 4; code integration không đồng nghĩa giao dịch sandbox
  đã được nghiệm thu.

