# Phase 3 - Giỏ hàng và đặt hàng COD

**Trạng thái:** Done
**Nhánh đề xuất:** `phase/03-cart-cod`
**Điều kiện bắt đầu:** Phase 2 Done; chốt phí vận chuyển COD và chính sách giữ/trừ tồn.

**Phạm vi đã duyệt:** backend-only; frontend do người dùng triển khai riêng theo OpenAPI. Mặc định phí
giao hàng 30.000 VND, miễn phí từ 1.000.000 VND, cấu hình qua env. COD trừ tồn khi tạo order; customer chỉ
được tự hủy khi còn `pending_confirmation`, sau đó tồn được hoàn đúng một lần.

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
| P03-S03-DB01 | DB | Order, OrderItem, status history, address/product/price snapshot | Tổng tiền decimal, snapshot không đổi theo catalog | Completed |
| P03-S03-BE01 | BE | `POST /api/v1/orders/` với idempotency key | Retry không tạo hai đơn | Completed |
| P03-S03-BE02 | BE | Khóa variant/tồn và trừ available trong transaction | Hai checkout đồng thời không oversell | Completed |
| P03-S03-FE01 | FE | Review, submit-once và confirmation page | Frontend do người dùng triển khai từ API handoff | External |
| P03-S03-TEST01 | Test | Race/idempotency/money tests | Tổng và tồn đúng dưới cạnh tranh | Completed |

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

## Kết quả backend

- Thêm app `orders` với cart, cart item, order, order item và lịch sử trạng thái; migration đã áp dụng vào
  PostgreSQL local.
- Cart luôn trả giá/tồn hiện hành. Quote và tạo order tải lại dữ liệu từ backend, không tin tổng tiền từ
  client.
- Tạo COD dùng `Idempotency-Key`, transaction và row lock tồn kho; retry cùng request trả lại order cũ,
  còn tái sử dụng key cho payload khác trả `409`.
- Order lưu snapshot địa chỉ, sản phẩm, SKU, size, màu và tiền; tạo order trừ tồn và xóa các cart item đã
  mua.
- Customer chỉ xem order của chính mình và chỉ tự hủy ở `pending_confirmation`; hủy hoàn tồn và ghi
  movement/history đúng một lần.
- Contract bàn giao frontend nằm tại [phase-03-backend-api.md](phase-03-backend-api.md), schema máy đọc ở
  `Base_dijango/schema.yml`.
- Toàn bộ 58 backend test pass trực tiếp trên PostgreSQL, gồm race test không oversell; coverage 89%.

Phase 3 được người dùng nghiệm thu khi cung cấp cấu hình và yêu cầu triển khai Phase 4 ngày 2026-09-15.
