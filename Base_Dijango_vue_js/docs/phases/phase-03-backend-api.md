# Phase 3 backend API handoff

Tài liệu này dành cho frontend Antigravity. Contract máy đọc là `Base_dijango/schema.yml`; JSON dùng
`snake_case`, URL có trailing slash, tiền VND được serialize thành chuỗi Decimal. Tất cả endpoint Phase 3
yêu cầu access token của user thuộc group `CUSTOMER`:

```http
Authorization: Bearer <access_token>
```

## Cart

| Method | Path | Request | Kết quả |
|---|---|---|---|
| GET | `/api/v1/cart/` | Không có | Cart, item hiện tại, giá, tồn, subtotal |
| POST | `/api/v1/cart/items/` | `{"variant": 12, "quantity": 2}` | Cart item mới hoặc tăng quantity, `201` |
| PATCH | `/api/v1/cart/items/{item_id}/` | `{"quantity": 3}` | Cart item sau cập nhật |
| DELETE | `/api/v1/cart/items/{item_id}/` | Không có | `204` |

`quantity` từ 1 đến 99. Backend từ chối variant không active/sản phẩm chưa publish hoặc quantity vượt tồn.
Cart không khóa giá: `variant.price`, `line_total` và `subtotal` luôn là giá catalog hiện hành. `item_id`
khác `variant_id`; PATCH/DELETE dùng ID của cart item.

## Checkout quote

`POST /api/v1/checkout/quote/`:

```json
{
  "address_id": 3,
  "cart_item_ids": [10, 11]
}
```

Response gồm `address_id`, `lines`, `subtotal`, `shipping_fee`, `discount_total`, `total`, `currency`.
Mỗi line có `cart_item_id`, variant/SKU, tên sản phẩm, size, màu, quantity, unit price và line total. Client
phải trình bày đúng quote mới nhất trước khi xác nhận; không tự gửi hoặc tự tính giá vào order request.

Phí mặc định là 30.000 VND và miễn phí khi subtotal từ 1.000.000 VND. Backend đọc
`SHIPPING_FLAT_FEE` và `FREE_SHIPPING_THRESHOLD` từ `.env`; frontend không hardcode chính sách này.

## Tạo đơn COD

`POST /api/v1/orders/` dùng cùng body với quote và bắt buộc header UUID ổn định cho một lần submit:

```http
Idempotency-Key: 7ad6a55b-b34e-4f45-af37-066e6ec440ab
```

- Lần đầu thành công trả `201`; retry cùng key và cùng payload trả order cũ với `200`.
- Cùng key nhưng đổi `address_id` hoặc `cart_item_ids` trả `409`.
- Frontend tạo UUID ngay trước submit, giữ nguyên UUID đó khi retry do timeout/mất mạng, và chỉ tạo UUID
  mới khi người dùng chủ động bắt đầu lần đặt hàng khác.
- Backend khóa tồn kho, kiểm tra lại giá/tồn, tạo snapshot, trừ tồn và xóa đúng các cart item đã mua trong
  một transaction. Không cần gọi API trừ tồn riêng.

Order khởi tạo với `status=pending_confirmation`, `payment_method=cod`, `payment_status=pending`. Response
chứa snapshot địa chỉ, các item, tổng tiền và `status_history`; dùng response này cho trang confirmation.

## Đơn của tôi và hủy đơn

| Method | Path | Kết quả |
|---|---|---|
| GET | `/api/v1/orders/` | `{count,next,previous,results}` theo mới nhất |
| GET | `/api/v1/orders/{order_id}/` | Order của user hiện tại |
| POST | `/api/v1/orders/{order_id}/cancel/` | Order đã hủy và tồn được hoàn |

Customer chỉ được tự hủy khi order còn `pending_confirmation`. Gọi hủy lại hoặc hủy sau khi trạng thái đã
đổi trả `409`; order của user khác trả `404` để không lộ dữ liệu.

## Xử lý lỗi và luồng frontend đề xuất

Lỗi dùng shape chung `{code,message,details,request_id}`. Các trường hợp UI cần xử lý rõ: `400` payload,
variant/tồn không hợp lệ; `401` cần đăng nhập/refresh; `403` không có role CUSTOMER; `404` address,
cart item hoặc order không thuộc user; `409` idempotency/hủy đơn xung đột.

Luồng đề xuất: tải cart → chọn item/address → lấy quote → hiển thị review → submit order một lần với UUID →
điều hướng confirmation từ order response. Swagger local ở `http://127.0.0.1:8000/api/docs/`.
