# Báo cáo khảo sát base

**Ngày khảo sát:** 2026-09-14  
**Phạm vi:** Phase 0A và baseline Phase 0B

## Hiện trạng

- Root `AGENTS.md` và hướng dẫn riêng cho frontend/backend đã được đọc.
- Backend là Django 5.2 + DRF modular monolith; hiện có `accounts` và `health`.
- Frontend là Vue 3 Composition API + TypeScript strict; hiện có login, home protected, profile và 404.
- Database dự kiến PostgreSQL; Redis dùng cho cache/throttle. Model dự án hiện chỉ có custom `User`.
- API dùng `/api/v1/`, trailing slash, JSON snake_case và error `code/message/details/request_id`.
- Auth dùng access JWT trong memory, refresh cookie HttpOnly, CSRF, rotation/blacklist và 401 retry một lần.
- Repository ở branch `main`; working tree sạch tại lúc khảo sát; `.env` backend được ignore.

## Có thể tái sử dụng

Auth/CSRF, API client/error handling, request ID/logging, settings theo môi trường, Docker Compose, OpenAPI,
CI, base UI/form components, route guards, test factories và conventions service/selector.

## Cần sửa hoặc đã chuẩn hóa trong Phase 0B

- OpenAPI trước đó chưa dùng error component chung cho các error status auth.
- Tài liệu logout mô tả cần access token nhưng source thực tế là logout CSRF-protected, idempotent.
- Cookie test so sánh trực tiếp `Morsel["secure"]` với boolean nên lỗi trên Windows khi flag false.
- ESLint/Prettier chưa ignore cache tool cục bộ; Prettier check phụ thuộc line ending của checkout Windows.
- Backend README có đường dẫn máy cá nhân và đường dẫn `uv` cục bộ không tồn tại trong repository.

## Còn thiếu theo nghiệp vụ

Registration/reset password, business roles, address, catalog, variant/SKU, inventory, cart, order, payment,
voucher, wishlist, review, exchange, recommendation events/algorithms, reporting và audit log.

## Phần chưa xác minh đầy đủ

- Docker Desktop không đưa daemon về trạng thái phản hồi trong phiên chạy này.
- PostgreSQL/Redis integration test và browser E2E chưa được chạy trên service thật.
- Pytest đã chạy bằng SQLite + LocMem để kiểm tra logic; đây không thay thế PostgreSQL/Redis verification.
- Chưa kiểm tra production deployment, SMTP, object storage, payment sandbox hoặc dữ liệu recommendation.

## Kết luận

Base phù hợp để mở rộng, chưa có lý do đổi stack hoặc viết lại. Domain mới nên tiếp tục theo modular
monolith và module frontend hiện hành; thay đổi kiến trúc lớn phải có ADR và approval riêng.

