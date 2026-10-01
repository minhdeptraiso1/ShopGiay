# Phase 2 backend API handoff

Tài liệu này dành cho frontend Antigravity. Nguồn contract máy đọc là `Base_dijango/schema.yml`; JSON dùng
`snake_case`, URL có trailing slash và list sản phẩm dùng pagination DRF `{count,next,previous,results}`.

## Xác thực và quyền

- Public: category, brand, size, color, product list/detail và event ingestion.
- ADMIN: toàn bộ CRUD catalog dưới `/api/v1/admin/`.
- STAFF hoặc ADMIN: điều chỉnh tồn và đọc stock movement.
- Access token gửi `Authorization: Bearer <access>`. Frontend không được dùng route guard thay backend role.

## Public catalog

| Method | Path | Mục đích |
|---|---|---|
| GET | `/api/v1/categories/` | Category active, không pagination |
| GET | `/api/v1/brands/` | Brand active, không pagination |
| GET | `/api/v1/sizes/?brand=nike` | Size active, tùy chọn lọc brand slug |
| GET | `/api/v1/colors/` | Color active, không pagination |
| GET | `/api/v1/products/` | Product published, search/filter/sort/pagination |
| GET | `/api/v1/products/{slug}/` | Chi tiết, gallery và variant public |

Query sản phẩm: `search`, `category`, `brand`, `size`, `color`, `min_price`, `max_price`, `in_stock` và
`ordering=newest|name|-name|price|-price`. Giá serialize thành chuỗi Decimal; `is_available` và tồn nằm ở
response backend, frontend không tự suy diễn từ variant ẩn.

## Admin catalog

Các resource `/api/v1/admin/categories/`, `brands/`, `products/`, `sizes/`, `colors/`, `variants/` và
`product-images/` hỗ trợ GET list/detail, POST, PUT, PATCH, DELETE. DELETE product/reference/variant là
soft deactivate. Variant và product-image list nhận query `product=<id>`.

Upload ảnh dùng `multipart/form-data` với `product`, `image`, `alt_text`, `sort_order`, `is_primary`.
Chấp nhận JPEG/PNG/WebP tối đa 5 MB. Response dùng `image_url`; không gửi field file base64 trong JSON.

Thứ tự tạo đề xuất: category → brand → size của brand → color → product draft → variant → image → publish
product → nhập tồn.

## Inventory

`POST /api/v1/admin/inventory/variants/{variant_id}/adjustments/`:

```json
{
  "delta": 10,
  "kind": "receipt",
  "reason": "Phiếu nhập NK-001"
}
```

`kind` là `receipt` hoặc `adjustment`; `delta` khác 0 và không được làm tồn âm. Response là movement có
`quantity_before`, `quantity_after`, actor và thời gian. Lịch sử đọc tại
`GET /api/v1/admin/inventory/variants/{variant_id}/movements/`.

## Event ingestion

`POST /api/v1/events/` nhận đúng các field allowlist:

```json
{
  "client_event_id": "b169dc2f-bef9-47aa-b078-bf9cbb7f55bf",
  "schema_version": 1,
  "event_type": "view",
  "source": "storefront",
  "product": 12,
  "anonymous_id": "f22df324-7830-4abd-aa34-44d592bf53a6",
  "recommendation_context_id": null
}
```

Event type: `view`, `recommendation_impression`, `recommendation_click`. Recommendation event bắt buộc có
`recommendation_context_id`. Guest bắt buộc có `anonymous_id`; user đăng nhập được gắn từ access token.
Gửi lại cùng `client_event_id` trả 200 và không tạo bản ghi thứ hai; lần đầu trả 201. Client không có quyền
gửi purchase event.

## Lỗi và OpenAPI

Lỗi theo shape chung `{code,message,details,request_id}` với 400/401/403/404/429 phù hợp. Swagger local:
`http://127.0.0.1:8000/api/docs/`; schema: `http://127.0.0.1:8000/api/schema/`.
