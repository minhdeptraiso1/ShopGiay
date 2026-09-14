# Phase 3 - Giỏ hàng và đặt hàng COD

**Trạng thái:** Planned  
**Nhánh đề xuất:** `phase/03-cart-cod`  
**Điều kiện bắt đầu:** Phase 2 Done; chốt phí vận chuyển COD và chính sách giữ/trừ tồn.

## Mục tiêu

CUSTOMER chọn variant, nhận báo giá do backend tính và tạo đơn COD nguyên tử, idempotent, không bán vượt tồn.

## Sprint 1 - Cart

- DB: `Cart`, `CartItem` unique theo cart+variant; quantity dương.
- API: `GET /api/v1/cart/`, `POST/PATCH/DELETE /api/v1/cart/items/...`.
- FE: mini cart, cart page, thay số lượng/xóa/chuyển checkout.
- Backend kiểm tra variant active/mua được và trả lại giá hiện hành; cart không phải price snapshot.

## Sprint 2 - Checkout quote

- API `POST /api/v1/checkout/quote/` nhận address, cart item IDs và trả subtotal, shipping, discount, total.
- Backend tải lại giá/tồn; FE chỉ trình bày kết quả và yêu cầu xác nhận khi giá/tồn thay đổi.
- Shipping ban đầu theo bảng cấu hình khu vực/giá trị đơn, không hardcode ở FE.

## Sprint 3 - COD order

| ID | Loại | Công việc | Đầu ra / nghiệm thu | Trạng thái |
|---|---|---|---|---|
| P03-S03-DB01 | DB | Order, OrderItem, status history, address/product/price snapshot | Tổng tiền decimal, snapshot không đổi theo catalog | Planned |
| P03-S03-BE01 | BE | `POST /api/v1/orders/` với idempotency key | Retry không tạo hai đơn | Planned |
| P03-S03-BE02 | BE | Khóa variant/tồn và trừ available trong transaction | Hai checkout đồng thời không oversell | Planned |
| P03-S03-FE01 | FE | Review, submit-once và confirmation page | Không double submit, lỗi tồn rõ ràng | Planned |
| P03-S03-TEST01 | Test | Race/idempotency/money tests | Tổng và tồn đúng dưới cạnh tranh | Planned |

## Sprint 4 - Đơn của tôi

- `GET /api/v1/orders/`, `GET /api/v1/orders/{id}/`, `POST .../{id}/cancel/`.
- Chỉ owner xem/hủy; STAFF/ADMIN dùng endpoint vận hành riêng ở Phase 4.
- Hủy chỉ ở trạng thái cho phép, ghi history và hoàn tồn đúng một lần.

## Trạng thái tối thiểu

`pending_confirmation -> confirmed -> preparing -> shipped -> completed`; nhánh `cancelled`. Payment COD
có trạng thái riêng `pending/paid/failed/refunded`, không đồng nhất với order status.

## Tiêu chí nghiệm thu

Luồng cart → quote → COD order → history/detail/cancel chạy FE-API-DB; backend tự tính tiền; snapshot đầy
đủ; ownership, idempotency và concurrent stock test pass.

