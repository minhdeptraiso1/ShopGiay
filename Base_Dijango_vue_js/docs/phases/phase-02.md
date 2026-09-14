# Phase 2 - Sản phẩm, biến thể và kho cơ bản

**Trạng thái:** Planned  
**Nhánh đề xuất:** `phase/02-catalog-inventory`  
**Điều kiện bắt đầu:** Phase 1 Done; chốt nơi lưu ảnh và quy tắc giá.

## Mục tiêu

Admin quản lý catalog và tồn theo SKU; khách xem/tìm/lọc sản phẩm public; hệ thống bắt đầu thu sự kiện xem.
Giá mặc định nằm ở variant, product hiển thị khoảng min-max.

## Sprint 1 - Catalog vertical slice

- DB: `Category`, `Brand`, `Product`, slug, trạng thái publish, mô tả và soft deactivate.
- BE: CRUD có permission; public list/detail chỉ trả sản phẩm publish.
- FE: admin list/form và storefront list/detail cơ bản.
- API dự kiến: `/api/v1/categories/`, `/brands/`, `/products/`, `/admin/products/`.
- Test: slug/unique, permission, hidden product, pagination và query count.

## Sprint 2 - Variant, ảnh và kho

| ID | Loại | Công việc | Đầu ra / nghiệm thu | Trạng thái |
|---|---|---|---|---|
| P02-S02-DB01 | DB | ProductImage, Size, Color, ProductVariant, InventoryBalance | SKU unique; quantity không âm; index product/status | Planned |
| P02-S02-DB02 | DB | StockMovement append-only | Mọi thay đổi tồn có lý do, actor, before/after | Planned |
| P02-S02-BE01 | BE | Variant/image CRUD, nhập và điều chỉnh tồn atomic | Chỉ permission phù hợp thao tác kho | Planned |
| P02-S02-FE01 | FE | Variant matrix, gallery và inventory UI | Chọn size/màu xác định đúng SKU/giá/tồn | Planned |
| P02-S02-TEST01 | Test | Constraint, permission, concurrent adjustment | Không âm tồn, không mất update | Planned |

## Sprint 3 - Discovery và event nền

- Search theo tên/SKU/brand/category; filter size, màu, giá, còn hàng; sort và pagination.
- `POST /api/v1/events/` nhận event frontend có allowlist; view event gắn anonymous session hoặc user.
- Purchase về sau chỉ được backend ghi, client không được tự khai báo mua thành công.
- UI có filter URL state, loading skeleton, empty/error và reset filter.

## Quy tắc và lỗi

- Không hard-delete sản phẩm/variant đã được tham chiếu; deactivate và giữ lịch sử.
- Size là thuộc tính theo brand/product; không suy diễn size hai thương hiệu tương đương.
- Public API không trả variant ẩn; hết hàng vẫn có thể xem nhưng không thể thêm giỏ.
- Upload phải kiểm tra loại/kích thước; production không mặc định dùng local filesystem nếu nhiều instance.

## Tiêu chí nghiệm thu

Admin tạo một sản phẩm có ảnh và nhiều variant, nhập kho, storefront tìm/lọc/chọn variant đúng, lịch sử tồn
đầy đủ, view event được ghi và toàn bộ API/permission/constraint có test.

## Cần chốt trước khi duyệt

Object storage/CDN, bộ size ban đầu, quy tắc variant price và ngưỡng tồn thấp. Mặc định: giá ở variant,
ảnh local chỉ cho development, cảnh báo tồn thấp cấu hình theo variant.

