# Phase 9 - Xác nhận giao và nhận hàng

**Trạng thái:** In progress

**Nhánh đề xuất:** `phase/09-delivery-confirmation`

**Điều kiện bắt đầu:** Phase 8 được nghiệm thu và realtime hoạt động.

## Mục tiêu

Hoàn thiện vòng đời giao hàng bằng state machine nội bộ, không tích hợp webhook hoặc hệ thống vận chuyển
bên thứ ba. Nhân viên xác nhận kiện hàng đã giao; khách hàng xác nhận đã nhận để hoàn tất đơn.

## Luồng trạng thái

1. STAFF/ADMIN chuyển đơn từ `preparing` sang `shipped` khi bắt đầu giao hàng.
2. Khi giao thành công, STAFF/ADMIN chuyển `shipped` sang `delivered` bằng nút **Xác nhận đã giao**.
3. Backend ghi người thao tác, thời gian, ghi chú và phát notification/WebSocket cho khách hàng.
4. Khách hàng bấm **Đã nhận hàng** để chuyển `delivered` sang `completed`.
5. Đơn COD chuyển sang đã thanh toán, cộng điểm một lần và cho phép khách đánh giá sản phẩm.

## Quy tắc nghiệp vụ

- CUSTOMER không được tự chuyển đơn sang `delivered`.
- STAFF/ADMIN không chuyển trực tiếp `shipped` sang `completed`.
- Khách chỉ xác nhận đơn của chính mình và chỉ khi trạng thái là `delivered`.
- Mọi chuyển trạng thái qua state machine, row lock và `expected_updated_at` để chống dữ liệu stale.
- Mỗi chuyển trạng thái ghi `OrderStatusHistory` và notification.
- Không có endpoint webhook, secret HMAC hoặc service vận chuyển giả lập.
- Không hoàn tiền trong flow này.

## Tiêu chí nghiệm thu

- STAFF/ADMIN nhìn thấy nút **Xác nhận đã giao** với đơn `shipped`.
- Thao tác hợp lệ chuyển đơn sang `delivered` và lưu đúng actor.
- Khách nhận cập nhật realtime, nhìn thấy nút **Đã nhận hàng** mà không phải tải lại.
- Khách xác nhận chuyển `delivered -> completed`; COD thành paid và điểm chỉ cộng một lần.
- CUSTOMER không truy cập API quản trị; trạng thái sai và cập nhật stale trả conflict.
