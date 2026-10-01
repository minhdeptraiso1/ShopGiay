# Phase 7 - Recommendation System

**Trạng thái:** Awaiting acceptance  
**Nhánh đề xuất:** `phase/07-recommendations`  
**Điều kiện bắt đầu:** Event schema từ Phase 2 đã vận hành; có dữ liệu hoặc dataset thử được gắn nhãn rõ.

## Nguyên tắc

- Không thêm microservice/ML infrastructure khi modular monolith và scheduled job đủ dùng.
- Purchase event chỉ sinh từ backend sau trạng thái nghiệp vụ được xác nhận.
- Mọi strategy có fallback và lọc product/variant không còn mua được.
- Kết quả từ sample data không được gọi là hiệu quả production.

## Sprint 1 - Data readiness và popular

- Audit coverage/duplication/latency của view, wishlist, add_cart, purchase, impression và click.
- DB/model cho interaction event, recommendation request/impression/click; index theo user/session/product/time.
- API `GET /api/v1/recommendations/popular/` và component storefront.
- Popular có time decay và fallback bestseller/catalog mới hợp lệ.

## Sprint 2 - Similar products

- Content features: category, brand, gender/style, material, color family và price band.
- Tính similarity offline/batch trong Django command/job; không so size giữa các brand như tương đương.
- API `GET /api/v1/products/{id}/recommendations/` có latency budget và fallback popular.

## Sprint 3 - Personalization và attribution

- Weighted implicit feedback: view < wishlist < add_cart < confirmed purchase.
- Anonymous theo random session; đăng nhập có thể hợp nhất trong giới hạn privacy đã chốt.
- `recommendation_request_id` liên kết impression/click; last eligible click 7 ngày cho cart/purchase.
- Dashboard tối thiểu: impressions, CTR, add-to-cart rate, purchase rate và coverage.

## Sprint 4 - Collaborative/hybrid có điều kiện

- Gate dữ liệu: đủ user/item active, interaction density và holdout evaluation có ý nghĩa.
- So sánh với baseline popular/content bằng Recall@K, NDCG@K, coverage và latency.
- Nếu không vượt baseline hoặc dữ liệu chưa đủ: ghi ADR hoãn, không triển khai phức tạp để đủ checklist.

## Privacy và retention

Chỉ lưu định danh cần thiết, không lưu secret/PII trong event payload; payload có allowlist/version; mặc định
raw event giữ 12 tháng rồi tổng hợp/xóa, subject deletion/anonymization theo policy được duyệt.

## Tiêu chí nghiệm thu

Popular, similar và personalized API/UI có fallback, lọc hàng hợp lệ, attribution test được; purchase không
thể giả từ client; metrics phân biệt offline/sample với production; latency và data-quality report có số liệu.

## Kết quả triển khai

- Catalog hỗ trợ ba loại `footwear`, `accessory`, `care`; size/màu chỉ bắt buộc với giày, còn hàng phụ
  kiện dùng `option_label` như `Freesize 39–44` hoặc `Chai 250 ml`.
- Seed catalog có 6 mẫu giày và 3 sản phẩm đi kèm: tất thể thao, bình xịt vệ sinh và bộ bàn chải.
- Có API popular, similar và personalized với fallback, lọc sản phẩm/SKU còn bán được và time decay.
- Trang chủ có rail phổ biến/cá nhân hóa; chi tiết giày ưu tiên chèn phụ kiện chăm sóc phù hợp.
- Impression/click liên kết `recommendation_request_id`; add-cart và purchase dùng last eligible click trong
  7 ngày. Client không được tự tạo purchase event.
- STAFF/ADMIN xem số liệu 30 ngày tại `/admin/recommendations`: request, impression, CTR, add-to-cart,
  purchase và coverage.

## Giới hạn có chủ đích

- Chưa triển khai collaborative filtering vì hiện chỉ có seed/sample data, chưa đủ interaction density để
  holdout evaluation có ý nghĩa. Weighted content/popular là baseline hiện hành; chỉ mở lại Sprint 4 khi
  có dữ liệu production và chứng minh Recall@K/NDCG@K tốt hơn baseline.
- Chưa chạy PostgreSQL integration/E2E trong lần triển khai này vì Docker của máy đang lỗi. Bộ test dùng
  SQLite/LocMem: 87 backend test pass (1 skip phụ thuộc PostgreSQL), 27 frontend test pass; Django/Ruff,
  migration drift, OpenAPI, targeted ESLint và production build đều pass. Cần chạy lại migration, seed và
  nghiệm thu UI trên PostgreSQL sau khi Docker hoạt động.

## Lệnh nghiệm thu sau khi Docker hoạt động

```powershell
cd Base_dijango
.\.tools\Scripts\uv.exe run python manage.py migrate
.\.tools\Scripts\uv.exe run python manage.py seed_catalog
.\.tools\Scripts\uv.exe run python manage.py runserver
```

Mở frontend và kiểm tra `/`, `/products/{slug}` và `/admin/recommendations`. Chạy lại `seed_catalog` là
idempotent, không tạo trùng dữ liệu mẫu.

