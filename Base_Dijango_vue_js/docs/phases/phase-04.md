# Phase 4 - Xử lý đơn và thanh toán online

**Trạng thái:** Planned  
**Nhánh đề xuất:** `phase/04-fulfillment-payment`  
**Điều kiện bắt đầu:** Phase 3 Done; chọn cổng thanh toán và có sandbox credentials.

## Sprint 1 - Staff fulfillment

- Admin/staff order queue, detail và transition actions theo permission.
- Backend state machine chặn chuyển trạng thái sai hoặc cập nhật stale.
- Ghi actor, thời gian, old/new status và ghi chú trong order status history/audit.
- CUSTOMER xem timeline giao hàng; không tự sửa trạng thái.

## Sprint 2 - Payment foundation

- DB: `Payment`, `PaymentAttempt`, `PaymentEvent`, `InventoryReservation` với provider reference unique.
- Tách order/payment/fulfillment status.
- Reservation có `expires_at`; job/command idempotent giải phóng giữ chỗ hết hạn.
- Secret chỉ qua env; payload nhạy cảm được lọc khỏi log.

## Sprint 3 - Online gateway

- `POST /api/v1/orders/{id}/payments/` tạo attempt và trả checkout URL/data.
- `POST /api/v1/payments/{provider}/webhook/` xác thực chữ ký trên raw body.
- Redirect frontend chỉ hiển thị trạng thái lấy lại từ backend, không xác nhận đã trả tiền.
- Webhook trùng/sai thứ tự/đến muộn phải idempotent; không trừ tồn hoặc ghi payment hai lần.
- Có reconciliation command/report cho event không khớp.

## Lỗi bắt buộc xử lý

Payment failed, user đóng trang, reservation hết hạn, webhook trùng, webhook đến sau khi hủy, số tiền hoặc
currency sai, provider timeout và thanh toán thành công nhưng response tạo checkout bị mất.

## Tiêu chí nghiệm thu

Staff xử lý COD đúng quyền; một giao dịch sandbox hoàn chỉnh từ checkout tới signed webhook; callback
không được tin; stock reservation được giải phóng; idempotency và out-of-order tests pass.

## Cần chốt trước khi duyệt

Provider, thời hạn giữ hàng, credential sandbox, callback domains và phí giao dịch. Nếu thiếu tài khoản,
Sprint 3 được đánh dấu Blocked, không dùng mock để tuyên bố tích hợp hoàn tất.

