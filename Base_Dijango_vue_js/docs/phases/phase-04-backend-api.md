# Phase 4 backend API handoff

Tài liệu này dành cho frontend Antigravity. Contract máy đọc là `Base_dijango/schema.yml`; JSON dùng
`snake_case`, URL có trailing slash, tiền VND là chuỗi Decimal. Không đưa VNPay hash secret vào frontend.

## Tạo order VNPay

`POST /api/v1/orders/` giữ nguyên `Idempotency-Key` UUID của Phase 3 và nhận thêm field optional
`payment_method`. Bỏ field hoặc gửi `cod` giữ nguyên luồng COD; thanh toán online gửi:

```json
{
  "address_id": 3,
  "cart_item_ids": [10, 11],
  "payment_method": "vnpay"
}
```

Backend tải lại giá/tồn, tạo order/payment và trừ available inventory dưới dạng reservation 15 phút.
Không gửi amount từ frontend. Order ban đầu là `pending_confirmation`, payment là `pending`.

## Tạo VNPay checkout

`POST /api/v1/orders/{order_id}/payment/` yêu cầu CUSTOMER là owner và header `Idempotency-Key` UUID mới
cho lần tạo checkout:

```json
{
  "locale": "vn",
  "bank_code": ""
}
```

Response `201` có `checkout_url`, `reference`, `status`, `expires_at`; retry cùng key/payload trả `200` và
attempt cũ. Cùng key nhưng đổi locale/bank trả `409`. Frontend chuyển browser tới `checkout_url`, không tự
ghép URL hoặc ký request.

VNPay redirect về `http://localhost:5173/payment/vnpay-return` kèm query. Trang return chỉ hiển thị trạng
thái lấy lại từ `GET /api/v1/orders/{order_id}/payment/`; không dùng `vnp_ResponseCode` trên browser để tự
xác nhận đã thanh toán.

## Payment status

`GET /api/v1/orders/{order_id}/payment/` trả payment owner-scoped với provider, status, amount, currency,
provider transaction number, paid time và attempts. Frontend có thể poll ngắn sau khi quay về từ VNPay.

Trạng thái payment: `pending`, `paid`, `failed`, `cancelled`, `refunded`. Attempt: `pending`, `succeeded`,
`failed`, `expired`, `cancelled`.

## VNPay IPN

`GET /api/v1/payments/vnpay/ipn/` là server-to-server public endpoint, không gọi từ frontend. Backend xác
minh HMAC-SHA512, `vnp_TmnCode`, amount, transaction status/reference và chống xử lý trùng. Provider phải
đăng ký URL public HTTPS trỏ tới endpoint này; `localhost` không nhận được callback từ VNPay sandbox.

## STAFF/ADMIN fulfillment

| Method | Path | Mục đích |
|---|---|---|
| GET | `/api/v1/admin/orders/?status=confirmed` | Queue phân trang, lọc trạng thái |
| GET | `/api/v1/admin/orders/{order_id}/` | Chi tiết order và customer email |
| POST | `/api/v1/admin/orders/{order_id}/transitions/` | Chuyển trạng thái có stale protection |

Payload transition:

```json
{
  "to_status": "preparing",
  "expected_updated_at": "2026-09-15T04:30:00Z",
  "note": "Đã đóng gói"
}
```

Luồng hợp lệ: `pending_confirmation → confirmed → preparing → shipped → completed`, với nhánh cancel
trước khi shipped. Client phải dùng `updated_at` mới nhất; stale hoặc transition sai trả `409`. VNPay chưa
paid chỉ được IPN xác nhận; VNPay đã paid không được hủy qua workflow hiện tại vì refund không nằm trong
roadmap. COD completed chuyển
payment status sang paid.

## Job vận hành

Chạy định kỳ mỗi phút:

```powershell
.\.tools\Scripts\uv.exe run python manage.py release_expired_reservations
```

Xem báo cáo cần đối soát:

```powershell
.\.tools\Scripts\uv.exe run python manage.py reconcile_vnpay_payments
```

Expiry/failure/hủy hoàn tồn đúng một lần; payment thành công capture reservation mà không trừ tồn lần hai.
Lỗi API ứng dụng giữ shape `{code,message,details,request_id}`; riêng IPN luôn trả JSON `RspCode/Message`
theo contract VNPay.
