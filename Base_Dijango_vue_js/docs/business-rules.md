# Quy tắc nghiệp vụ xuyên suốt

## Tài khoản và quyền

- Guest không là role database; CUSTOMER, STAFF và ADMIN là role bundle dự kiến bằng Django Groups.
- Đặt hàng mặc định yêu cầu đăng nhập.
- Backend luôn kiểm tra permission và ownership; route guard hoặc ẩn nút chỉ hỗ trợ UX.
- Tài khoản inactive không được login, refresh hoặc dùng protected API.

## Catalog, giá và tồn

- Variant là đơn vị mua hàng, có SKU, size, màu, giá và tồn riêng.
- Tiền dùng decimal và mã tiền ISO; backend là nguồn tính giá cuối cùng.
- Không coi size giữa các thương hiệu là tương đương nếu chưa có bảng quy đổi được duyệt.
- Không hard-delete sản phẩm/variant đã được giao dịch tham chiếu.
- Mọi thay đổi tồn có movement, actor, reason và transaction; quantity không âm.

## Cart, order và payment

- Cart không khóa giá; checkout và order phải tải lại giá/tồn ở backend.
- Order item lưu snapshot tên, SKU, size, màu, unit price và discount allocation.
- Tạo đơn, payment attempt, webhook và yêu cầu đổi hàng phải idempotent.
- Order, payment và fulfillment có state riêng; redirect frontend không xác nhận đã thanh toán.
- COD trừ tồn nguyên tử khi tạo đơn; online giữ tồn có expiry, theo quyết định chính thức ở Phase 4.

## Voucher và đổi hàng

- Voucher được kiểm tra lại khi đặt hàng và không được vượt usage limit khi concurrent.
- Giảm giá phân bổ xuống order line để lưu đúng giá trị thực của từng sản phẩm đã mua.
- Đổi hàng theo order line và quantity, chỉ sang variant khác thuộc cùng sản phẩm.
- Chỉ hàng đã nhận và qua inspection là bán lại được mới hoàn tồn available.
- Đổi hàng giữ nguyên giá trị đã thanh toán; hệ thống không thu thêm hoặc hoàn chênh lệch.
- Không triển khai trả hàng lấy tiền, refund COD hoặc refund qua cổng thanh toán.

## Recommendation và privacy

- Thu view, wishlist, add_cart, confirmed purchase, impression và click từ sớm.
- Purchase event chỉ do backend sinh sau xác nhận nghiệp vụ.
- Recommendation luôn lọc sản phẩm ẩn/không mua được và có fallback.
- Event payload có allowlist/version, không chứa secret hay PII không cần thiết.
- Attribution mặc định là last eligible recommendation click trong 7 ngày; retention raw mặc định 12 tháng,
  chờ duyệt chính sách chính thức.

