# Phase 4 - Xử lý đơn và thanh toán online

**Trạng thái:** Done (cấu hình sandbox E2E được hoãn)
**Nhánh đề xuất:** `phase/04-fulfillment-payment`
**Điều kiện bắt đầu:** Phase 3 Done; chọn cổng thanh toán và có sandbox credentials.

**Phạm vi đã duyệt:** provider VNPay sandbox 2.1.0, reservation 15 phút; backend triển khai trước và
frontend được tích hợp bổ sung ngày 2026-09-29. Secret chỉ nằm trong `.env` local và phải được rotate do
đã từng được chia sẻ trong hội thoại.

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

## Kết quả backend hiện tại

- Hoàn tất staff/admin order queue, detail và transition state machine có `expected_updated_at`, row lock,
  permission và status history.
- Thêm payment, attempt, event và inventory reservation; order VNPay giữ available stock 15 phút, capture
  khi IPN paid và hoàn đúng một lần khi fail/cancel/expiry.
- Tạo URL VNPay 2.1.0 bằng query đã sort và HMAC-SHA512; IPN xác minh checksum, merchant, amount,
  transaction reference, trạng thái và xử lý trùng/sai thứ tự.
- Thêm command `release_expired_reservations` và `reconcile_vnpay_payments`; secret chỉ nằm trong `.env`
  local đã Git ignore.
- Migration `catalog.0003`, `orders.0002` và `orders.0003` đã áp dụng vào PostgreSQL local. 68 backend test pass trực tiếp
  trên PostgreSQL, coverage 89%; Ruff, Django checks, migration drift và OpenAPI validation pass.
- Contract frontend nằm tại [phase-04-backend-api.md](phase-04-backend-api.md).
- Frontend checkout đã cho chọn COD/VNPay, tự tạo payment attempt cho đơn VNPay và chỉ hiển thị CTA thanh
  toán lại trên đúng đơn VNPay chưa thanh toán. STAFF đã đọc được SKU để vận hành kho mà không có quyền
  thay đổi catalog.

## Note công việc VNPay hoãn lại

Code và luồng frontend/backend đã sẵn sàng, nhưng cấu hình sandbox và giao dịch end-to-end chưa được thực
hiện vì VNPay không gọi được IPN `localhost`. Theo quyết định ngày 2026-09-29, phần vận hành này được hoãn
để chuyển sang Phase 5; trạng thái `Done` chỉ xác nhận phạm vi code, không có nghĩa sandbox đã pass.

Trước release phải hoàn thành:

1. Mở public HTTPS URL/tunnel cho backend.
2. Đăng ký `https://<public-backend>/api/v1/payments/vnpay/ipn/` tại merchant sandbox.
3. Thực hiện giao dịch test và xác minh IPN cập nhật `paid`, capture reservation đúng một lần.
4. Xác minh payment fail/expiry giải phóng tồn và chạy reconciliation không còn event bất thường.
