# Tiến độ dự án

## Trạng thái hiện tại

| Phase | Trạng thái | Ghi chú |
|---|---|---|
| Phase 0 | Done | Đã được duyệt khi người dùng yêu cầu bắt đầu Phase 1 |
| Phase 1 | Done | Đã được duyệt khi người dùng yêu cầu chuyển sang Phase 2 |
| Phase 2 | Done | Đã được duyệt khi người dùng yêu cầu bắt đầu Phase 3 |
| Phase 3 | Done | Đã được duyệt khi người dùng cung cấp cấu hình và yêu cầu làm Phase 4 |
| Phase 4 | Done | Fulfillment và code VNPay hoàn tất; cấu hình/kiểm thử sandbox E2E được hoãn |
| Phase 5 | Awaiting acceptance | Đã code voucher, wishlist, review, banner và frontend; chờ nghiệm thu |
| Phase 6 | Awaiting acceptance | Đã code exchange-only và VNPay return về đúng trang đơn; chờ nghiệm thu |
| Phase 7 | Awaiting acceptance | Recommendation và catalog phụ kiện đã code; chờ Docker/PostgreSQL để nghiệm thu |
| Phase 8-9 | Planned | Chưa được duyệt triển khai |

## Nhật ký

### 2026-09-14 - Phase 0A

- Đọc source, repository instructions, standards, manifests, settings, auth, routing, model, migration và CI.
- Không sửa source hoặc truy cập dữ liệu trong lần khảo sát đầu tiên.
- Lập roadmap và tạo file kế hoạch Phase 0-9.

### 2026-09-14 - Phase 0B

- Cài backend/frontend từ lockfile bằng uv 0.8.22 và pnpm 11.19.0; không nâng manifest.
- Backend lint, format, Django check, migration drift và OpenAPI validation pass.
- Pytest fallback SQLite/LocMem: 23 passed, coverage 90%.
- Frontend typecheck, ESLint, Prettier, 10 Vitest tests và production build pass.
- Chuẩn hóa OpenAPI auth error component, tài liệu logout, cookie test Windows và tool cache/line ending.
- Docker daemon chưa phản hồi; PostgreSQL/Redis pytest và browser E2E còn chưa xác minh.

### 2026-09-14 - Phase 1

- Thêm đăng ký customer, role bundle bằng Django Groups và backend permission cho admin shell.
- Thêm reset mật khẩu token một lần với phản hồi chống dò email và cấu hình email theo môi trường.
- Thêm address model, constraint một default/user và CRUD owner-scoped.
- Thêm storefront/admin layouts, các trang auth/địa chỉ/403 cùng route guard theo role.
- Migration rehearsal pass; backend 33 test/91% coverage; frontend 16 test; Playwright 4 luồng desktop/mobile.
- OpenAPI, README và quyết định kiến trúc được đồng bộ với contract Phase 1.

### 2026-09-14 - Phase 2 backend

- Thêm catalog, variant, media metadata, tồn kho/movement và product interaction event.
- Public discovery API hỗ trợ search/filter/sort/pagination; admin CRUD và inventory API có role protection.
- Tạo tài liệu API handoff riêng cho frontend Antigravity; không sửa source frontend trong Phase 2.
- Migration rehearsal SQLite pass; 47 backend test pass, coverage 88%; OpenAPI và static gates pass.
- PostgreSQL row-lock concurrency và object storage production chưa được tích hợp thật.

### 2026-09-14 - Phase 3 backend

- Thêm cart, checkout quote, COD order, snapshot và lịch sử trạng thái; chỉ CUSTOMER truy cập dữ liệu của
  chính mình.
- Tạo order có idempotency key, transaction/row lock tồn kho, trừ tồn nguyên tử và chặn oversell.
- Hủy `pending_confirmation` hoàn tồn đúng một lần; giá, phí giao hàng và tổng tiền do backend tính.
- Migration catalog/orders đã áp dụng vào PostgreSQL local; tài khoản demo đã tồn tại và có role CUSTOMER.
- Bàn giao contract riêng cho frontend Antigravity; không sửa source frontend trong Phase 3.
- 58 backend test pass trực tiếp trên PostgreSQL, bao gồm concurrency test; coverage 89%, OpenAPI và static
  gates pass.

### 2026-09-15 - Phase 4 backend

- Thêm STAFF/ADMIN order queue và state transition có permission, stale protection, row lock và audit.
- Thêm VNPay payment/attempt/event, inventory reservation 15 phút, signed checkout URL và verified IPN.
- Thêm expiry/reconciliation commands; SMTP Gmail và VNPay sandbox đọc từ `.env` local bị Git ignore.
- Migration catalog/orders đã áp dụng; 68 test pass trên PostgreSQL, coverage 89%, OpenAPI/static gates pass.
- Còn chờ public HTTPS IPN URL để chạy một giao dịch VNPay sandbox end-to-end; Phase 4 vẫn `In progress`.

### 2026-09-29 - Phase 4 frontend và vận hành

- STAFF đọc được danh sách SKU phục vụ màn kho, nhưng vẫn không được tạo/sửa/xóa biến thể catalog.
- Form sản phẩm, danh mục, thương hiệu và màu tự sinh slug tiếng Việt qua helper dùng chung.
- Checkout cho chọn COD hoặc VNPay; đơn VNPay tạo payment attempt và chuyển sang sandbox, đơn COD không
  còn hiển thị nút thanh toán VNPay sai nghiệp vụ.
- 22 backend tests liên quan catalog/checkout/VNPay và 24 frontend tests pass; typecheck và production
  build pass.

### 2026-09-29 - Chốt Phase 4 và chuẩn bị Phase 5

- Người dùng quyết định chuyển sang Phase 5 và hoãn cấu hình VNPay sandbox end-to-end.
- Phase 4 được đánh dấu `Done` theo phạm vi code; việc mở public HTTPS IPN URL, đăng ký merchant sandbox và
  xác minh giao dịch thật được giữ thành deferred operational task, không ghi nhận là đã pass.
- Phase 5 chuyển sang `Awaiting approval`; chưa triển khai cho tới khi có yêu cầu bắt đầu rõ ràng.

### 2026-09-29 - Phase 5

- Thêm voucher có thời hạn, minimum spend, scope, giới hạn toàn cục/theo khách, reservation và phân bổ
  discount theo line; checkout frontend hỗ trợ áp/bỏ mã.
- Thêm wishlist owner-scoped cùng event backend, trang wishlist và nút yêu thích ở list/detail.
- Thêm review verified-purchase, public approved-only và màn moderation cho STAFF/ADMIN.
- Thêm banner có lịch/vị trí, storefront slot và màn quản trị dành riêng cho ADMIN.
- Thêm seed `WELCOME10`/banner demo và đã áp dụng migration/seed trên PostgreSQL local; OpenAPI,
  Django/Ruff/migration checks, 75 backend test trên PostgreSQL và 25 frontend test pass; frontend
  production build pass.

### 2026-09-29 - Điều chỉnh phạm vi Phase 6

- Người dùng quyết định Phase 6 chỉ làm đổi hàng, không làm trả hàng lấy tiền hoặc hoàn tiền.
- Phạm vi mới chỉ cho đổi size/màu trong cùng sản phẩm, giữ nguyên giá trị đã thanh toán và không xử lý
  chênh lệch tiền.
- Loại bỏ Refund/RefundAttempt, refund VNPay, hoàn COD và thông tin tài khoản nhận tiền khỏi roadmap.

### 2026-09-29 - Phase 6

- Thêm exchange state machine FE-API-DB, customer ownership, STAFF/ADMIN queue, idempotency, stale
  protection và status history.
- Thêm reservation cho variant thay thế, stock movement giữ/hoàn/nhập lại và command tự giải phóng yêu
  cầu hết hạn; tuyệt đối không tạo luồng refund.
- VNPay dùng return URL động cùng origin để quay về đúng trang chi tiết đơn; UI chờ IPN xác nhận trước khi
  báo đã thanh toán và tự xóa query VNPay khỏi URL.
- Đã lưu merchant sandbox mới trong `.env` local bị Git ignore; không ghi TmnCode/secret vào source hoặc
  tài liệu. Public HTTPS IPN và giao dịch sandbox thật vẫn cần cấu hình ở Merchant Admin.
- Migration đã áp dụng PostgreSQL local; 81 backend test và 27 frontend test pass; OpenAPI/Ruff/Django
  check, frontend typecheck và production build pass.

### 2026-09-29 - Hoàn thiện xác nhận VNPay và nhận hàng

- Thêm endpoint xác minh signed VNPay return cho môi trường local chưa nhận được IPN; dùng cùng kiểm tra
  checksum/merchant/amount/reference và processor idempotent với IPN.
- Thêm customer action `confirm-received` chỉ cho đơn của chính khách ở trạng thái `shipped`; sau xác nhận
  đơn thành `completed`, COD thành `paid` và sản phẩm đủ điều kiện đánh giá.
- UI thêm nút **Đã nhận được hàng**, hộp thoại xác nhận và liên kết đánh giá theo từng order item.
- 84 backend test, 27 frontend test, OpenAPI validation và frontend production build pass.

### 2026-09-29 - Hoàn thiện UX nội dung và khuyến mãi

- Sửa lỗi 500 khi duyệt/từ chối đánh giá trên PostgreSQL bằng transaction nguyên tử cho thao tác khóa
  dòng; bổ sung regression test chạy ngoài test transaction.
- Voucher được tách thành màn danh sách và màn tạo/chỉnh sửa; danh sách hiển thị trạng thái lịch chạy,
  mức giảm, lượt dùng và thời hạn.
- Banner được tổ chức thành lịch đăng riêng, nhãn vị trí/trạng thái, form đăng độc lập và khung xem trước
  trước khi lưu.

### 2026-09-29 - Loyalty, voucher tự chọn và giao hàng đổi

- Đơn chuyển sang `completed` được cộng một lần số điểm bằng 0,5% tổng thanh toán, làm tròn số nguyên;
  có tài khoản điểm và sổ giao dịch chống cộng trùng. Migration cũng cấp điểm cho đơn đã hoàn tất.
- Voucher có ngưỡng điểm tối thiểu; checkout tự tải các voucher vừa đủ điểm vừa hợp lệ với giỏ hiện tại,
  khách chọn trực tiếp và không còn phải gõ mã. Điểm là điều kiện hạng thành viên, áp mã không trừ điểm.
- Banner trang chủ hiển thị một nội dung tại một thời điểm, tự chuyển sau 7 giây, có nút chọn và tôn trọng
  tùy chọn giảm chuyển động; khu banner được chuyển xuống dưới dải chữ chạy.
- Đơn gốc vẫn giữ `completed`. Yêu cầu đổi có trạng thái `replacement_shipped`, mã vận đơn và lịch sử
  riêng; khách xác nhận đã nhận sản phẩm đổi để kết thúc, không tạo `Order` mới và không hoàn tiền.

## Công việc hoãn lại/giới hạn hiện tại

- Email production chưa thể gửi thật nếu chưa cung cấp SMTP/provider credentials; local tự in nội dung
  email ra terminal backend.
- Frontend Phase 4 đã tích hợp; còn cần nghiệm thu trực quan giao dịch sandbox end-to-end.
- VNPay sandbox chưa được kiểm thử end-to-end vì IPN không thể gọi localhost. Khi quay lại cần HTTPS
  tunnel/domain, đăng ký IPN tại merchant portal và xác minh trạng thái paid/capture reservation.

## Bước tiếp theo

1. Sau khi Docker hoạt động, migrate và chạy `seed_catalog` để nghiệm thu giày, tất và sản phẩm vệ sinh.
2. Nghiệm thu popular/personalized trên trang chủ, sản phẩm tương tự/đi kèm ở trang chi tiết và dashboard
   `/admin/recommendations`.
3. Mở public HTTPS IPN URL, khai báo trong Merchant Admin và chạy giao dịch VNPay sandbox bằng thẻ test.

### 2026-09-30 - Phase 7 và catalog phụ kiện

- Mở rộng catalog để bán giày, phụ kiện và sản phẩm chăm sóc; biến thể ngoài giày không bị ép size/màu.
- Bổ sung seed tất thể thao, bình xịt vệ sinh và bộ bàn chải; storefront/cart/order hiển thị quy cách SKU.
- Triển khai popular, similar và personalized recommendation có fallback và chèn sản phẩm đi kèm vào
  recommendation chi tiết giày.
- Bổ sung request/rank, impression/click, attribution add-cart/purchase 7 ngày và dashboard metrics cho
  STAFF/ADMIN; purchase event chỉ do backend tạo.
- Collaborative filtering được hoãn có chủ đích đến khi có dữ liệu production đủ để đánh giá offline.
- Docker/PostgreSQL đang lỗi theo thông báo của người dùng nên chưa chạy integration/E2E; kiểm tra local
  dùng SQLite/LocMem: 87 backend test pass (1 PostgreSQL-only skip), 27 frontend test pass; Django/Ruff,
  migration drift, OpenAPI, targeted ESLint và production build pass. Sẽ chạy lại trên PostgreSQL khi môi
  trường sẵn sàng.
