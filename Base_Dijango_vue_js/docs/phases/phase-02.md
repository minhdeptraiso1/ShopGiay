# Phase 2 - Sản phẩm, biến thể và kho cơ bản

**Trạng thái:** Done
**Nhánh đề xuất:** `phase/02-catalog-inventory`  
**Điều kiện bắt đầu:** Phase 1 Done; chốt nơi lưu ảnh và quy tắc giá.

**Phạm vi triển khai đã duyệt:** backend-only. Frontend do người dùng thực hiện bằng Antigravity Code;
OpenAPI và tài liệu handoff là hợp đồng tích hợp. Giá nằm ở variant, tiền tệ VND; file ảnh dùng local media
trong development, production cần object storage/CDN trước khi triển khai nhiều instance.

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
| P02-S02-DB01 | DB | ProductImage, Size, Color, ProductVariant, InventoryBalance | SKU unique; quantity không âm; index product/status | Completed |
| P02-S02-DB02 | DB | StockMovement append-only | Mọi thay đổi tồn có lý do, actor, before/after | Completed |
| P02-S02-BE01 | BE | Variant/image CRUD, nhập và điều chỉnh tồn atomic | Chỉ permission phù hợp thao tác kho | Completed |
| P02-S02-FE01 | FE | Variant matrix, gallery và inventory UI | Người dùng tự triển khai bằng Antigravity theo OpenAPI | External |
| P02-S02-TEST01 | Test | Constraint, permission, concurrent adjustment | Không âm tồn; row lock đã triển khai, PostgreSQL concurrency chưa chạy | Partial |

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

Với phạm vi backend-only đã duyệt, phần màn hình storefront/admin được thay bằng OpenAPI và
[tài liệu bàn giao API](phase-02-backend-api.md) để người dùng triển khai frontend riêng.

## Kết quả backend

- Thêm module `catalog` và migration cho category, brand, product, image, size theo brand, color, variant,
  inventory balance, stock movement và product event.
- Public API chỉ trả sản phẩm published thuộc category/brand active; hỗ trợ search, filter size/màu/giá/tồn,
  sort và pagination, đồng thời prefetch để tránh N+1.
- Admin CRUD yêu cầu ADMIN; điều chỉnh tồn và xem movement cho STAFF/ADMIN. Product/variant/reference data
  được deactivate thay vì hard-delete; movement không có API sửa/xóa.
- Điều chỉnh tồn dùng transaction và row lock, từ chối tồn âm, ghi actor/reason/before/after. Giá variant là
  Decimal, currency bị ràng buộc VND và size phải thuộc cùng brand với product.
- Ảnh giới hạn JPEG/PNG/WebP, tối đa 5 MB và một ảnh primary/product. Development phục vụ local media.
- Event endpoint chỉ nhận allowlist view/recommendation, schema version 1, UUID chống ghi trùng và không cho
  client khai báo purchase.
- Backend suite 47 test pass, coverage 88%; Ruff, Django check, migration drift/rehearsal và OpenAPI pass.
- PostgreSQL/Redis integration và kiểm tra concurrent row locking thật chưa được chạy vì PostgreSQL Docker
  chưa sẵn sàng; SQLite rehearsal không chứng minh hành vi lock của PostgreSQL.

## Cần chốt trước khi duyệt

Object storage/CDN, bộ size ban đầu, quy tắc variant price và ngưỡng tồn thấp. Mặc định: giá ở variant,
ảnh local chỉ cho development, cảnh báo tồn thấp cấu hình theo variant.

## Approval gate

Phase 2 được người dùng nghiệm thu khi yêu cầu bắt đầu Phase 3 ngày 2026-09-14.
