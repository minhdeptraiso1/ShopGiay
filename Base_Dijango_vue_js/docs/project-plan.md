# Kế hoạch dự án website bán giày

## Mục tiêu

Phát triển website bán giày một cửa hàng trên base Django REST Framework + Vue 3 hiện có, gồm storefront,
quản trị, mua hàng, thanh toán, đổi hàng và recommendation. Không đổi stack hoặc tách microservice nếu chưa
có bằng chứng và approval.

## Nguồn kế hoạch

- [Mục lục phase](phases/README.md)
- [Phase 0 - Khảo sát và chuẩn hóa base](phases/phase-00.md)
- [Phase 1 - Tài khoản, phân quyền và khung UI](phases/phase-01.md)
- [Phase 2 - Sản phẩm, biến thể và kho](phases/phase-02.md)
- [Phase 3 - Giỏ hàng và COD](phases/phase-03.md)
- [Phase 4 - Xử lý đơn và thanh toán](phases/phase-04.md)
- [Phase 5 - Khuyến mãi và tương tác](phases/phase-05.md)
- [Phase 6 - Đổi hàng](phases/phase-06.md)
- [Phase 7 - Recommendation System](phases/phase-07.md)
- [Phase 8 - Báo cáo và vận hành](phases/phase-08.md)
- [Phase 9 - Release readiness](phases/phase-09.md)

## Approval gates

Mỗi phase đi qua `Planned -> Awaiting approval -> In progress -> Awaiting acceptance -> Done`. Chỉ câu
xác nhận rõ như `Duyệt Phase 2` mới cho phép bắt đầu Phase 2. Duyệt roadmap không duyệt triển khai toàn bộ.

## Kiến trúc giữ lại

- Monorepo hai ứng dụng, backend modular monolith và frontend module theo nghiệp vụ.
- PostgreSQL, Redis, Django ORM/migration, DRF, Vue Router, Pinia và API client chung.
- JWT access trong memory, refresh cookie HttpOnly, CSRF và response/error contract hiện tại.
- Quality gates và CI hiện có; mỗi phase bổ sung test theo rủi ro nghiệp vụ.

## Quyết định chưa chốt

Email provider, object storage/CDN, payment gateway, shipping policy/provider, exchange window,
data retention và điều kiện đủ dữ liệu cho collaborative filtering phải được chốt trước phase liên quan.

