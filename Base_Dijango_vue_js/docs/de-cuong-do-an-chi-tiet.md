# ĐỀ CƯƠNG CHI TIẾT BÁO CÁO ĐỒ ÁN

## Xây dựng website bán giày và phụ kiện Hải Duy Shop

> Tài liệu này là nguồn nội dung để đưa cho ChatGPT biên soạn thành báo cáo Word hoàn chỉnh. Những trường
> đặt trong dấu `[ ... ]` cần được người làm đồ án bổ sung trước khi tạo bản chính thức.

---

## 1. Thông tin chung cần điền

| Nội dung | Giá trị |
|---|---|
| Trường | `[Tên trường]` |
| Khoa/Bộ môn | `[Tên khoa hoặc bộ môn]` |
| Tên đề tài | Xây dựng website bán giày và phụ kiện Hải Duy Shop |
| Sinh viên thực hiện | `[Họ và tên sinh viên]` |
| Mã sinh viên | `[Mã sinh viên]` |
| Lớp | `[Tên lớp]` |
| Giảng viên hướng dẫn | `[Họ và tên giảng viên]` |
| Loại báo cáo | `[Đồ án tốt nghiệp/Khóa luận/Đồ án chuyên ngành]` |
| Địa điểm, năm | `[Địa điểm], 2026` |

## 2. Yêu cầu đối với bản Word được tạo

Khi chuyển đề cương này thành Word, cần tuân thủ các yêu cầu sau:

- Ngôn ngữ: tiếng Việt, văn phong học thuật, rõ ràng, không dùng giọng quảng cáo.
- Không tự bịa kết quả kiểm thử, số liệu kinh doanh, số người dùng hoặc thông tin triển khai production.
- Phân biệt rõ chức năng đã xây dựng, chức năng đang nghiệm thu và định hướng tương lai.
- Độ dài đề xuất: 65–90 trang nội dung chính, không tính phụ lục.
- Khổ giấy A4; font Times New Roman; cỡ chữ 13; giãn dòng 1,3–1,5.
- Tiêu đề chương cỡ 16–18, in hoa/in đậm; tiêu đề mục cỡ 13–14, in đậm.
- Căn lề tham khảo: trái 3–3,5 cm; phải 2 cm; trên 2–2,5 cm; dưới 2–2,5 cm.
- Đánh số chương, mục, hình và bảng tự động bằng Heading/Caption của Word.
- Tạo mục lục, danh mục hình, danh mục bảng và danh mục từ viết tắt tự động.
- Mỗi hình/bảng phải có số thứ tự, tên và đoạn nhận xét/giải thích phía sau.
- Mã nguồn chỉ trích đoạn ngắn để minh họa; mã dài đưa xuống phụ lục.
- Trích dẫn tài liệu theo chuẩn `[IEEE/APA theo yêu cầu của trường]`.
- Ảnh giao diện dùng ảnh chụp thật của hệ thống; vị trí cần ảnh được đánh dấu trong đề cương.

---

# PHẦN ĐẦU BÁO CÁO

## Trang bìa và trang phụ bìa

- Tên trường, khoa/bộ môn.
- Tên loại đồ án.
- Tên đề tài.
- Họ tên sinh viên, mã sinh viên, lớp.
- Giảng viên hướng dẫn.
- Địa điểm và năm thực hiện.

## Lời cam đoan

Nêu rõ sản phẩm và báo cáo do sinh viên thực hiện; các nội dung tham khảo đều được trích dẫn; sinh viên
chịu trách nhiệm về tính trung thực của kết quả.

## Lời cảm ơn

Cảm ơn giảng viên hướng dẫn, khoa/bộ môn, gia đình, bạn bè và các cá nhân hỗ trợ. Viết ngắn gọn trong
khoảng nửa đến một trang.

## Nhận xét của giảng viên

Để trống theo mẫu của trường.

## Mục lục

Tạo tự động từ Heading 1–3 trong Word.

## Danh mục từ viết tắt

| Từ viết tắt | Ý nghĩa |
|---|---|
| API | Application Programming Interface |
| CRUD | Create, Read, Update, Delete |
| CSRF | Cross-Site Request Forgery |
| DB | Database – Cơ sở dữ liệu |
| DRF | Django REST Framework |
| E2E | End-to-End Testing |
| HMAC | Hash-based Message Authentication Code |
| HTTP/HTTPS | Hypertext Transfer Protocol/Secure |
| IPN | Instant Payment Notification |
| JWT | JSON Web Token |
| RBAC | Role-Based Access Control |
| REST | Representational State Transfer |
| SKU | Stock Keeping Unit |
| SPA | Single Page Application |
| UI/UX | User Interface/User Experience |
| UML | Unified Modeling Language |
| VNPay | Cổng thanh toán điện tử VNPay |
| WebSocket | Giao thức kết nối hai chiều theo thời gian thực |

## Tóm tắt đề tài

Viết khoảng 300–500 từ, bao gồm:

- Bối cảnh nhu cầu kinh doanh giày và phụ kiện trực tuyến.
- Vấn đề cần giải quyết: quản lý catalog nhiều biến thể, tồn kho theo SKU, đơn hàng, thanh toán, đổi hàng,
  khuyến mãi và chăm sóc khách hàng.
- Giải pháp: hệ thống web gồm Django REST Framework, Vue 3, PostgreSQL và Redis.
- Các điểm nổi bật: RBAC, VNPay, voucher, đổi hàng không hoàn tiền, recommendation, báo cáo lợi nhuận,
  realtime và luồng xác nhận giao/nhận hàng.
- Phương pháp đánh giá: kiểm thử API, component, E2E, phân quyền, idempotency và concurrency.
- Kết quả chính và giới hạn còn tồn tại.

## Abstract

Dịch phần tóm tắt sang tiếng Anh, dùng đúng thuật ngữ kỹ thuật và không bổ sung ý mới.

---

# MỞ ĐẦU

## 1. Lý do chọn đề tài

Trình bày các ý:

- Thương mại điện tử giúp cửa hàng mở rộng kênh bán hàng và phục vụ khách không phụ thuộc địa điểm.
- Sản phẩm giày có nhiều size, màu và mức tồn khác nhau nên quản lý bằng sản phẩm tổng quát là chưa đủ.
- Cửa hàng cần đồng bộ bán hàng, tồn kho, khuyến mãi, thanh toán, đổi hàng và báo cáo trên một hệ thống.
- Trải nghiệm người dùng cần có tìm kiếm, lọc, yêu thích, đánh giá và gợi ý sản phẩm phù hợp.
- Các giao dịch quan trọng phải đảm bảo an toàn, không bán vượt tồn và không xử lý trùng callback.

## 2. Mục tiêu đề tài

### 2.1. Mục tiêu tổng quát

Xây dựng một website bán giày và phụ kiện hoàn chỉnh cho một cửa hàng, hỗ trợ khách hàng mua sắm trực
tuyến và hỗ trợ nhân viên/quản trị viên vận hành catalog, kho, đơn hàng, khuyến mãi, đổi hàng và báo cáo.

### 2.2. Mục tiêu cụ thể

- Xây dựng hệ thống tài khoản, xác thực và phân quyền CUSTOMER/STAFF/ADMIN.
- Quản lý sản phẩm, danh mục, thương hiệu, ảnh, size, màu và biến thể SKU.
- Quản lý tồn kho có lịch sử biến động, phiếu nhập, giá vốn bình quân và cảnh báo tồn thấp.
- Xây dựng giỏ hàng, báo giá, đặt hàng COD và thanh toán VNPay.
- Đảm bảo tạo đơn, thanh toán, voucher và callback thanh toán có tính idempotent.
- Hỗ trợ wishlist, voucher, điểm tích lũy, banner và đánh giá đã xác minh mua hàng.
- Hỗ trợ đổi size/màu trong cùng sản phẩm, không thực hiện hoàn tiền.
- Xây dựng recommendation phổ biến, tương tự, cá nhân hóa và sản phẩm đi kèm.
- Xây dựng báo cáo doanh thu, giá vốn, lợi nhuận, tồn kho và hiệu quả gợi ý.
- Cập nhật realtime cho đơn hàng, đổi hàng, kho và thông báo.
- Hoàn thiện luồng nhân viên xác nhận đã giao và khách hàng xác nhận đã nhận.

## 3. Đối tượng và phạm vi nghiên cứu

### 3.1. Đối tượng nghiên cứu

- Quy trình kinh doanh của cửa hàng giày và phụ kiện.
- Kiến trúc ứng dụng web SPA kết nối REST API.
- Quản lý giao dịch, tồn kho và vòng đời đơn hàng.
- Xác thực, phân quyền và bảo mật API.
- Gợi ý sản phẩm dựa trên dữ liệu hành vi.
- Cơ chế realtime và callback thanh toán server-to-server.

### 3.2. Phạm vi chức năng

- Storefront cho khách và CUSTOMER.
- Không gian vận hành cho STAFF.
- Không gian quản trị đầy đủ cho ADMIN.
- Catalog gồm giày, phụ kiện và sản phẩm chăm sóc giày.
- Thanh toán COD và VNPay sandbox.
- Đổi size/màu trong cùng sản phẩm.
- Báo cáo và xuất Excel nhiều sheet.
- Quản lý vòng đời giao/nhận hàng ngay trong hệ thống.

### 3.3. Ngoài phạm vi

- Không xây dựng marketplace nhiều nhà bán hàng.
- Không hoàn tiền COD hoặc VNPay.
- Không đổi sang sản phẩm khác loại; chỉ đổi biến thể cùng sản phẩm.
- Không tích hợp hãng vận chuyển production hoặc theo dõi GPS.
- Không triển khai collaborative filtering do chưa đủ dữ liệu production.
- Không triển khai production chính thức trong phạm vi hiện tại.

## 4. Phương pháp thực hiện

- Khảo sát quy trình bán hàng và yêu cầu nghiệp vụ.
- Phân tích use case, state machine và mô hình dữ liệu.
- Thiết kế modular monolith và frontend theo module nghiệp vụ.
- Phát triển theo từng phase, có migration và API contract.
- Kiểm thử tự động ở backend/frontend và kiểm thử tích hợp thủ công.
- Đánh giá kết quả, hạn chế và đề xuất hướng phát triển.

## 5. Bố cục báo cáo

Tóm tắt nội dung năm chương:

1. Tổng quan bài toán và khảo sát hệ thống.
2. Cơ sở lý thuyết và công nghệ sử dụng.
3. Phân tích và thiết kế hệ thống.
4. Xây dựng và triển khai các chức năng.
5. Kiểm thử, đánh giá và hướng phát triển.

---

# CHƯƠNG 1. TỔNG QUAN VÀ KHẢO SÁT BÀI TOÁN

## 1.1. Giới thiệu cửa hàng và bài toán quản lý

- Mô tả mô hình cửa hàng bán giày, phụ kiện và sản phẩm chăm sóc.
- Mô tả đặc điểm sản phẩm giày: nhiều size, màu, SKU và lượng tồn riêng.
- Trình bày các nghiệp vụ bán hàng, nhập kho, thanh toán, giao hàng, đổi hàng và khuyến mãi.
- Nêu khó khăn khi quản lý thủ công hoặc bằng dữ liệu rời rạc.

## 1.2. Khảo sát quy trình hiện tại

Mô tả quy trình giả định trước khi có hệ thống:

1. Khách xem sản phẩm qua cửa hàng hoặc kênh mạng xã hội.
2. Nhân viên kiểm tra tồn kho thủ công.
3. Đơn hàng và thanh toán được ghi nhận rời rạc.
4. Khó theo dõi voucher, lịch sử đổi hàng và lợi nhuận thực.
5. Khách chưa nhận được gợi ý hoặc thông báo trạng thái đồng nhất.

## 1.3. Các vấn đề cần giải quyết

| Vấn đề | Hệ quả | Giải pháp trong đề tài |
|---|---|---|
| Không quản lý tồn theo SKU | Dễ bán nhầm size/màu hoặc vượt tồn | Variant và InventoryBalance theo SKU |
| Giá/tổng tiền do client gửi | Có nguy cơ sai lệch hoặc bị sửa | Backend tính lại toàn bộ báo giá |
| Callback có thể gửi trùng | Trừ tồn/cập nhật trạng thái nhiều lần | Idempotency key và event ID unique |
| Phân quyền chỉ ở giao diện | Có thể truy cập API trái phép | Permission và ownership tại backend |
| Khó xác định lợi nhuận | Thiếu giá vốn lịch sử | Giá vốn bình quân và snapshot lúc bán |
| Khách khó tìm sản phẩm phù hợp | Giảm trải nghiệm mua sắm | Search/filter và recommendation |
| Phải tải lại trang để xem trạng thái | Trải nghiệm chậm | Django Channels, Redis và WebSocket |

## 1.4. Nhóm người dùng

### 1.4.1. Khách chưa đăng nhập

- Xem trang chủ, catalog và chi tiết sản phẩm.
- Tìm kiếm, lọc và xem đánh giá đã duyệt.
- Đăng ký, đăng nhập và quên mật khẩu.

### 1.4.2. Khách hàng – CUSTOMER

- Quản lý hồ sơ và địa chỉ.
- Dùng giỏ hàng, voucher, wishlist và đặt hàng.
- Thanh toán, theo dõi đơn, xác nhận nhận hàng và đánh giá.
- Theo dõi điểm tích lũy và yêu cầu đổi hàng.

### 1.4.3. Nhân viên – STAFF

- Xử lý đơn hàng theo trạng thái được phép.
- Theo dõi/điều chỉnh kho, lập phiếu nhập.
- Duyệt đánh giá và xử lý đổi hàng.
- Xem một số báo cáo vận hành không nhạy cảm.

### 1.4.4. Quản trị viên – ADMIN

- Có toàn bộ khả năng của STAFF.
- Quản lý catalog, voucher, banner và tài khoản nhân viên.
- Xem doanh thu, giá vốn, lợi nhuận và audit log.
- Không dùng `is_superuser` thay cho role nghiệp vụ ADMIN.

## 1.5. Yêu cầu chức năng tổng quát

Lập bảng yêu cầu với các nhóm mã:

- `FR-AUTH`: tài khoản, đăng nhập, refresh token, reset mật khẩu.
- `FR-CATALOG`: danh mục, thương hiệu, sản phẩm, SKU, ảnh, size, màu.
- `FR-INVENTORY`: tồn kho, biến động, nhập hàng, giá vốn.
- `FR-CART`: giỏ hàng và báo giá.
- `FR-ORDER`: đặt hàng, trạng thái và lịch sử.
- `FR-PAYMENT`: COD, VNPay và IPN.
- `FR-ENGAGEMENT`: voucher, wishlist, review, banner, loyalty.
- `FR-EXCHANGE`: đổi hàng.
- `FR-RECOMMENDATION`: gợi ý và attribution.
- `FR-REPORT`: báo cáo và Excel.
- `FR-REALTIME`: thông báo và cập nhật realtime.
- `FR-DELIVERY`: xác nhận đã giao và đã nhận hàng.

## 1.6. Yêu cầu phi chức năng

- Bảo mật: JWT, HttpOnly cookie, CSRF, CORS, RBAC, ownership và HMAC.
- Toàn vẹn: transaction, row lock, constraint, idempotency và audit trail.
- Hiệu năng: pagination server-side, select/prefetch related, cache Redis khi phù hợp.
- Khả dụng: loading/empty/error state, responsive, dark/light và thông báo rõ ràng.
- Bảo trì: modular monolith, module frontend theo nghiệp vụ và OpenAPI.
- Khả năng kiểm thử: pytest, Vitest, Playwright, factory và môi trường test riêng.
- Quan sát: request ID, logging, audit log và health endpoint.

## 1.7. Kết luận chương

Tóm tắt yêu cầu và dẫn sang cơ sở lý thuyết/công nghệ được chọn.

---

# CHƯƠNG 2. CƠ SỞ LÝ THUYẾT VÀ CÔNG NGHỆ

## 2.1. Kiến trúc ứng dụng web

- Mô hình client–server.
- SPA và REST API.
- Modular monolith và lý do phù hợp hơn microservice ở quy mô đề tài.
- JSON, HTTP method và status code.

## 2.2. Backend Django và Django REST Framework

- Django 5.2: ORM, migration, transaction, authentication và admin nền tảng.
- Django REST Framework 3.16: APIView, serializer, permission, pagination và throttling.
- drf-spectacular và OpenAPI/Swagger.
- Django-environ quản lý cấu hình theo môi trường.

## 2.3. Frontend Vue 3 và TypeScript

- Vue 3 Composition API và Single File Component.
- TypeScript strict giúp phát hiện lỗi kiểu dữ liệu.
- Vue Router cho định tuyến và route guard.
- Pinia quản lý auth/cart/toast/theme state.
- Axios API client, interceptor access/refresh token.
- Vite và Tailwind CSS.
- Vee Validate kết hợp Zod cho validation biểu mẫu.

## 2.4. PostgreSQL và Redis

### 2.4.1. PostgreSQL

- Cơ sở dữ liệu quan hệ, khóa ngoại, unique/check constraint và index.
- Transaction ACID và `SELECT ... FOR UPDATE`.
- Lý do phù hợp với đơn hàng, tồn kho và thanh toán.

### 2.4.2. Redis

- Cache, channel layer và giao tiếp realtime.
- Vai trò của Redis trong Django Channels.

## 2.5. Xác thực và phân quyền

- JWT access token ngắn hạn.
- Refresh token lưu trong cookie HttpOnly.
- CSRF protection cho request dùng cookie.
- RBAC bằng Django Groups và permission.
- Ownership: người dùng chỉ truy cập tài nguyên của chính mình.
- Phân biệt route guard giao diện với kiểm tra quyền thực sự ở backend.

## 2.6. WebSocket và hệ thống realtime

- Khác biệt giữa HTTP request/response và WebSocket.
- ASGI, Daphne, Django Channels và Redis channel layer.
- Ticket ngắn hạn để xác thực kết nối WebSocket.
- Notification lưu database với trạng thái đã đọc/chưa đọc.

## 2.7. Thanh toán VNPay

- Luồng tạo payment URL, redirect, return URL và IPN.
- HMAC-SHA512 xác minh dữ liệu VNPay.
- Không tin redirect từ trình duyệt để xác nhận đã thanh toán.
- Reservation tồn kho và xử lý callback trùng/sai thứ tự.

## 2.8. Callback thanh toán và HMAC

- Khái niệm callback/IPN server-to-server.
- HMAC-SHA512 bảo đảm tính xác thực và toàn vẹn dữ liệu VNPay.
- Không dựa vào dữ liệu redirect phía trình duyệt để xác nhận thanh toán.
- Mã giao dịch và payment event bảo đảm xử lý callback idempotent.

## 2.9. Quản lý tồn kho và giá vốn

- SKU là đơn vị tồn kho nhỏ nhất.
- Stock movement theo hướng append-only.
- Công thức giá vốn bình quân gia quyền:

```text
Giá vốn bình quân mới =
  (Tồn cũ × Giá vốn cũ + Số lượng nhập × Giá nhập mới)
  / (Tồn cũ + Số lượng nhập)
```

- Snapshot giá vốn tại thời điểm bán.
- Công thức lợi nhuận trong phạm vi đề tài:

```text
Lợi nhuận = Doanh thu thuần - Giá vốn hàng bán
```

- Chưa tính phí vận chuyển và phí VNPay vào lợi nhuận.

## 2.10. Hệ thống recommendation

- Popular recommendation có time decay.
- Content-based similarity theo danh mục, thương hiệu, thuộc tính và mức giá.
- Personalized recommendation dựa trên implicit feedback.
- Trọng số tương tác: view < wishlist < add_cart < confirmed purchase.
- Fallback khi không đủ dữ liệu.
- Impression, click, CTR, add-to-cart, purchase và coverage.
- Lý do chưa dùng collaborative filtering: dữ liệu production chưa đủ để đánh giá Recall@K/NDCG@K.

## 2.11. Công nghệ kiểm thử và chất lượng mã nguồn

- Pytest, pytest-django, factory-boy và coverage.
- Vitest và Vue Test Utils.
- Playwright cho E2E.
- Ruff, ESLint, Prettier và TypeScript typecheck.
- OpenAPI validation và migration drift check.

## 2.12. Kết luận chương

Tổng kết lý do lựa chọn stack và liên hệ với các yêu cầu chương 1.

---

# CHƯƠNG 3. PHÂN TÍCH VÀ THIẾT KẾ HỆ THỐNG

## 3.1. Kiến trúc tổng thể

Mô tả sơ đồ triển khai logic:

```text
Trình duyệt Vue 3
    |-- HTTPS/REST --> Django REST Framework --> PostgreSQL
    |-- WebSocket --> Django Channels --------> Redis
                              |
                              |-- SMTP email
                              |-- VNPay sandbox
```

Giải thích trách nhiệm từng thành phần và lý do không tách thành nhiều microservice.

## 3.2. Phân rã module

### Backend

- `accounts`: user, role, địa chỉ, reset mật khẩu và điểm tích lũy.
- `catalog`: category, brand, product, variant, ảnh, tồn kho và phiếu nhập.
- `orders`: cart, order, payment, reservation, fulfillment và lịch sử trạng thái.
- `engagement`: voucher, wishlist, review và banner.
- `exchanges`: quy trình đổi hàng và reservation sản phẩm thay thế.
- `recommendations`: interaction, request, rank, attribution và metrics.
- `notifications`: thông báo database và WebSocket.
- `operations`: báo cáo, quản lý nhân viên và audit log.
- `health`: kiểm tra tình trạng dịch vụ.

### Frontend

- App/router/stores dùng chung.
- Layout storefront, auth và admin/staff.
- Module auth, profile, address, catalog, cart, order, engagement, exchange, recommendation,
  notification và admin.
- Component dùng chung: input, button, dialog, pagination, alert, toast và theme toggle.

## 3.3. Biểu đồ use case tổng quát

Vẽ bốn actor: Guest, CUSTOMER, STAFF, ADMIN. Use case tối thiểu:

- Guest: xem/tìm/lọc sản phẩm, xem đánh giá, đăng ký, đăng nhập.
- CUSTOMER: quản lý địa chỉ, giỏ hàng, wishlist, voucher, đặt hàng, thanh toán, theo dõi, xác nhận nhận,
  đánh giá, đổi hàng và xem điểm.
- STAFF: xử lý đơn, kho, nhập hàng, review moderation và đổi hàng.
- ADMIN: catalog, khuyến mãi, banner, nhân viên, báo cáo tài chính và audit.
- Hệ thống ngoài: VNPay và SMTP.

**Hình cần chèn:** `Hình 3.1 – Biểu đồ use case tổng quát`.

## 3.4. Đặc tả use case quan trọng

Mỗi use case trình bày: mã, tác nhân, tiền điều kiện, hậu điều kiện, luồng chính và luồng ngoại lệ.

### UC-01 – Đăng ký và đăng nhập

- Đăng ký công khai chỉ tạo CUSTOMER.
- Tài khoản inactive không đăng nhập hoặc refresh được.
- Access token lưu trong memory; refresh token trong HttpOnly cookie.

### UC-02 – Tìm kiếm và lựa chọn sản phẩm

- Tìm theo tên/SKU/thương hiệu/danh mục.
- Lọc size, màu, giá và còn hàng.
- Chọn đúng variant trước khi thêm giỏ.

### UC-03 – Đặt hàng COD

- CUSTOMER chọn địa chỉ và cart item.
- Backend kiểm tra lại giá/tồn, tính phí và voucher.
- Tạo đơn trong transaction, trừ tồn và lưu snapshot.
- Retry cùng idempotency key không tạo đơn thứ hai.

### UC-04 – Thanh toán VNPay

- Tạo payment attempt và URL ký.
- Người dùng thanh toán tại sandbox.
- Backend chỉ ghi nhận paid sau khi xác minh dữ liệu ký.
- Callback lặp không capture tồn hai lần.

### UC-05 – Xử lý đơn hàng

- STAFF chuyển trạng thái theo state machine.
- Request chứa `expected_updated_at` để ngăn cập nhật stale.
- Mỗi chuyển trạng thái tạo history và notification.

### UC-06 – Đổi hàng

- Chỉ đơn completed và còn trong thời hạn đổi.
- Target variant phải cùng product.
- Duyệt, nhận, kiểm hàng, giữ tồn, giao sản phẩm thay thế và xác nhận hoàn tất.
- Không tạo đơn mới và không hoàn tiền.

### UC-07 – Đánh giá sản phẩm

- Chỉ order item đủ điều kiện mới được đánh giá.
- STAFF/ADMIN duyệt hoặc từ chối.
- Storefront chỉ hiển thị review approved.

### UC-08 – Xác nhận giao và nhận hàng

- STAFF/ADMIN xác nhận đơn `shipped` đã được giao để chuyển sang `delivered`.
- Backend kiểm tra quyền, trạng thái hiện tại và `expected_updated_at` để tránh cập nhật stale.
- Mỗi lần chuyển trạng thái tạo lịch sử, thông báo và sự kiện realtime.
- CUSTOMER sở hữu đơn bấm “Đã nhận hàng” để chuyển `delivered` sang `completed`.

## 3.5. Thiết kế trạng thái đơn hàng

```text
pending_confirmation
    -> confirmed
    -> preparing
    -> shipped
    -> delivered
    -> completed

pending_confirmation/confirmed/preparing -> cancelled (khi hợp lệ)
```

Giải thích:

- `shipped -> delivered` do STAFF/ADMIN xác nhận đã giao.
- `delivered -> completed` do khách xác nhận đã nhận.
- COD chuyển paid khi hoàn tất.
- VNPay có payment status riêng, không đồng nhất với order status.

**Hình cần chèn:** `Hình 3.2 – State machine đơn hàng`.

## 3.6. Thiết kế trạng thái đổi hàng

```text
pending -> approved -> received -> inspected
        -> replacement_ready -> replacement_shipped -> completed

pending/approved -> rejected hoặc cancelled theo điều kiện
```

Nêu quy tắc reservation, inspection, nhập lại hàng đủ điều kiện và giải phóng tồn khi thất bại/hết hạn.

**Hình cần chèn:** `Hình 3.3 – State machine đổi hàng`.

## 3.7. Thiết kế cơ sở dữ liệu

Chia ERD thành các cụm để hình không quá dày:

### 3.7.1. Tài khoản và phân quyền

- User, Group, Permission, Address.
- LoyaltyAccount, LoyaltyTransaction.
- Password reset token `[nếu trình bày theo source thực tế]`.

### 3.7.2. Catalog và kho

- Category, Brand, Product, ProductImage.
- Size, Color, ProductVariant.
- InventoryBalance, StockMovement.
- InventoryReceipt, InventoryReceiptLine.

### 3.7.3. Bán hàng và thanh toán

- Cart, CartItem.
- Order, OrderItem, OrderStatusHistory.
- Payment, PaymentAttempt, PaymentEvent.
- InventoryReservation.

### 3.7.4. Tương tác và hậu mãi

- Voucher, VoucherUsage/Reservation/Allocation.
- Wishlist, Review, Banner.
- ExchangeRequest, ExchangeItem, ExchangeReservation, ExchangeStatusHistory.
- Notification.

### 3.7.5. Recommendation và vận hành

- InteractionEvent/ProductEvent.
- RecommendationRequest, RecommendationRank/Impression/Click/Attribution.
- AuditLog.

Với mỗi bảng chính, mô tả mục đích, khóa chính, khóa ngoại, trường quan trọng và constraint nghiệp vụ.

**Hình cần chèn:**

- `Hình 3.4 – ERD tài khoản và catalog`.
- `Hình 3.5 – ERD đơn hàng và thanh toán`.
- `Hình 3.6 – ERD tương tác, đổi hàng và recommendation`.

## 3.8. Thiết kế API

Trình bày nguyên tắc:

- Prefix `/api/v1/`.
- JSON field dùng English `snake_case`.
- Pagination mặc định 20 dòng/trang.
- Error response thống nhất có code, message/detail và request ID.
- API bảo vệ bằng JWT/permission/ownership; VNPay IPN dùng chữ ký riêng.

Nhóm endpoint tiêu biểu:

| Nhóm | Endpoint minh họa | Chức năng |
|---|---|---|
| Auth | `/api/v1/auth/login/`, `/refresh/`, `/me/` | Phiên đăng nhập |
| Catalog | `/api/v1/products/`, `/products/{slug}/` | Danh sách/chi tiết công khai |
| Cart | `/api/v1/cart/`, `/cart/items/` | Quản lý giỏ |
| Checkout | `/api/v1/checkout/quote/` | Báo giá từ backend |
| Order | `/api/v1/orders/` | Tạo/xem đơn của khách |
| Payment | `/api/v1/orders/{id}/payment/` | Tạo thanh toán VNPay |
| VNPay | `/api/v1/payments/vnpay/ipn/` | IPN có chữ ký |
| Engagement | `/api/v1/wishlist/`, `/vouchers/`, `/reviews/` | Tương tác khách hàng |
| Exchange | `/api/v1/exchanges/` | Đổi hàng |
| Recommendation | `/api/v1/recommendations/popular/` | Gợi ý sản phẩm |
| Notification | `/api/v1/notifications/` | Đọc/chưa đọc |
| Admin | `/api/v1/admin/...` | Vận hành và quản trị |

## 3.9. Thiết kế bảo mật

- Password hash bởi Django, không lưu plaintext.
- Không cho client tự gán role STAFF/ADMIN.
- Secret nằm trong `.env`, không commit Git.
- Refresh cookie HttpOnly, SameSite và Secure theo môi trường.
- CSRF/CORS/Allowed Hosts cấu hình rõ.
- Hạn chế login, refresh, reset password và event bằng throttle.
- Upload ảnh kiểm tra MIME và kích thước.
- HMAC và dữ liệu giao dịch cho VNPay/IPN.
- Audit các hành động quản trị quan trọng.
- Log không ghi password, token hoặc secret.

## 3.10. Thiết kế giao diện

Nêu các nguyên tắc:

- Responsive cho desktop/tablet/mobile.
- Hỗ trợ light/dark mode.
- Giao diện storefront và admin có layout riêng.
- Toàn bộ nhãn người dùng bằng tiếng Việt.
- Có trạng thái loading, empty, error và success.
- Form có label, validation và thông báo rõ.
- Bảng quản trị có search, filter, phân trang và thao tác nhất quán.

Liệt kê wireframe/màn hình cần trình bày:

- Trang chủ, sản phẩm, chi tiết, giỏ hàng, checkout.
- Đăng nhập/đăng ký/hồ sơ/địa chỉ.
- Danh sách và chi tiết đơn.
- Wishlist và đổi hàng.
- Dashboard, quản lý catalog, kho, đơn, tương tác, báo cáo, nhân viên và audit.
- Chi tiết đơn với thao tác xác nhận đã giao và xác nhận đã nhận hàng.

## 3.11. Kết luận chương

Tóm tắt thiết kế và dẫn sang chương hiện thực hệ thống.

---

# CHƯƠNG 4. XÂY DỰNG HỆ THỐNG

## 4.1. Môi trường và cấu trúc dự án

### Công nghệ chính

| Thành phần | Công nghệ |
|---|---|
| Backend | Python 3.12+, Django 5.2, DRF 3.16 |
| Frontend | Vue 3.5, TypeScript 5.9, Vite 7 |
| Database | PostgreSQL |
| Realtime/cache | Redis, Django Channels, Daphne |
| API docs | OpenAPI, drf-spectacular, Swagger UI |
| Payment | VNPay sandbox 2.1.0 |
| Report | openpyxl, Excel `.xlsx` nhiều sheet |
| Test | pytest, Vitest, Playwright |
| Tooling | uv, pnpm, Ruff, ESLint, Prettier |

### Cấu trúc monorepo

```text
Base_Dijango_vue_js/
├── Base_dijango/         Django REST backend
├── frontend/             Vue SPA
└── docs/                 Tài liệu kiến trúc và phase
```

## 4.2. Xây dựng tài khoản và phân quyền

- Seed các group CUSTOMER/STAFF/ADMIN idempotent.
- Đăng ký chỉ gán CUSTOMER.
- Login, refresh, logout và `auth/me`.
- Reset mật khẩu token một lần; SMTP nếu cấu hình, nếu không in local terminal.
- CRUD địa chỉ theo ownership; tối đa một địa chỉ mặc định.
- Admin quản lý STAFF nhưng không tự nâng quyền trái phép.

**Ảnh cần chèn:** đăng nhập, đăng ký, hồ sơ, địa chỉ và popup thêm nhân viên.

## 4.3. Xây dựng catalog và kho

- Quản lý category, brand, size, color, product, image và variant.
- Slug tự sinh từ tên, hỗ trợ tiếng Việt.
- Giày bắt buộc size/màu; phụ kiện có quy cách như freesize hoặc chai 250 ml.
- Public API chỉ trả sản phẩm published.
- Điều chỉnh tồn nguyên tử, không cho quantity âm.
- Phiếu nhập thủ công hoặc CSV gồm:
  `Mã SKU, Số lượng, Giá nhập/đơn vị, Ngày nhập, Nhà cung cấp, Ghi chú`.
- Tải file mẫu rỗng, xuất danh sách hiện tại và import lại.
- Tính giá vốn bình quân và lưu movement.

**Ảnh cần chèn:** quản lý sản phẩm, form SKU, thiết lập catalog, kho và popup nhập hàng.

## 4.4. Xây dựng giỏ hàng và COD

- Cart unique theo user; CartItem unique theo cart+variant.
- Backend trả giá và tồn hiện tại, không khóa giá tại cart.
- Quote tính subtotal, shipping, discount và total.
- Phí giao mặc định 30.000 VND, miễn phí từ 1.000.000 VND, cấu hình bằng env.
- Tạo đơn dùng transaction, row lock và `Idempotency-Key`.
- OrderItem lưu snapshot tên, SKU, size, màu, giá, giảm giá và giá vốn.
- Hủy đúng trạng thái sẽ hoàn tồn đúng một lần.

**Ảnh cần chèn:** giỏ hàng, checkout COD, danh sách và chi tiết đơn.

## 4.5. Xử lý đơn và VNPay

- STAFF chuyển trạng thái theo state machine.
- `expected_updated_at` chống thao tác trên dữ liệu stale.
- PaymentAttempt và PaymentEvent tách khỏi Order.
- Online order giữ tồn có expiry; paid capture, fail/cancel/expiry giải phóng.
- VNPay URL được ký HMAC-SHA512.
- IPN/return kiểm tra checksum, merchant, amount, reference và trạng thái.
- Return URL quay lại đúng trang chi tiết đơn.
- Command giải phóng reservation và reconciliation.

**Lưu ý trung thực:** code VNPay đã hoàn thiện nhưng sandbox E2E qua public HTTPS IPN vẫn là hạng mục
phải nghiệm thu trước release.

## 4.6. Voucher, wishlist, review, banner và loyalty

### Voucher

- Thời gian hiệu lực, minimum spend, category/product scope.
- Global/per-user usage limit.
- Reservation/redemption/release.
- Phân bổ giảm giá theo order line bằng largest remainder.
- Checkout tự liệt kê voucher đủ điều kiện và đủ ngưỡng điểm.

### Wishlist

- Unique user+product và ownership.
- Ghi event sau khi mutation thành công.

### Review

- Verified purchase theo order item.
- Moderation pending/approved/rejected.
- Public approved-only.

### Banner

- Lịch bắt đầu/kết thúc, vị trí, ưu tiên, light/dark.
- Trang chủ hiển thị từng banner và tự chuyển theo thời gian.

### Loyalty

- Cộng một lần 0,5% giá trị đơn hoàn tất, làm tròn số nguyên.
- Sổ giao dịch chống cộng trùng.
- Điểm chỉ là điều kiện voucher, không bị trừ khi áp mã.

## 4.7. Quy trình đổi hàng

- Chỉ đổi size/màu của cùng sản phẩm.
- Không hoàn tiền và không tạo đơn hàng mới.
- CUSTOMER chọn order item, số lượng và target variant.
- STAFF duyệt, nhận, kiểm tra, chuẩn bị và giao đổi.
- Reservation giữ variant thay thế; tự hoàn khi hết hạn/hủy.
- Chỉ hàng đạt kiểm tra mới nhập lại available stock.
- Yêu cầu đổi có mã vận đơn và timeline riêng.
- Khách xác nhận nhận hàng đổi để completed.

**Ảnh cần chèn:** form yêu cầu đổi, danh sách đổi của khách và màn xử lý đổi của STAFF.

## 4.8. Recommendation System

- Thu view, wishlist, add_cart, purchase, impression và click.
- Purchase chỉ do backend sinh sau nghiệp vụ thành công.
- Popular có time decay và fallback.
- Similar dựa trên feature sản phẩm.
- Personalized dựa trên implicit feedback.
- Chi tiết giày ưu tiên phụ kiện chăm sóc phù hợp.
- Attribution click gần nhất trong cửa sổ 7 ngày.
- Dashboard có request, impression, CTR, add-to-cart, purchase và coverage.

**Ảnh cần chèn:** rail gợi ý trang chủ, gợi ý chi tiết sản phẩm và dashboard recommendation.

## 4.9. Báo cáo và vận hành

- Dashboard tổng quan lấy aggregate thật.
- Báo cáo doanh thu, tồn kho, đổi hàng và recommendation.
- Doanh thu/giá vốn/lợi nhuận chỉ ADMIN được xem.
- Xuất một file Excel nhiều sheet thay vì nhiều CSV rời.
- Quản lý nhân viên bằng popup.
- Audit log append-only cho thao tác quản trị.
- Pagination/filter/search/date/today đồng nhất ở màn quản trị.

**Ảnh cần chèn:** dashboard, biểu đồ doanh thu, báo cáo, nhân viên và audit log.

## 4.10. Realtime và notification

- Notification lưu DB với `is_read` và thời điểm tạo.
- Chuông thông báo ở header storefront/admin.
- WebSocket ticket có thời hạn.
- Khi đơn, đổi hàng hoặc kho thay đổi, UI tự tải lại dữ liệu liên quan.
- Không dùng WebSocket làm nguồn sự thật thay database.

## 4.11. Xác nhận giao và nhận hàng

### Luồng vận hành

1. STAFF/ADMIN chuyển đơn sang `shipped` khi bắt đầu giao hàng.
2. Khi giao thành công, STAFF/ADMIN bấm “Xác nhận đã giao” để chuyển đơn sang `delivered`.
3. Backend lưu status history, gửi notification và phát sự kiện realtime.
4. CUSTOMER bấm “Đã nhận hàng” để chuyển đơn sang `completed`.
5. Với COD, hệ thống ghi nhận thanh toán thành công khi đơn hoàn tất; điểm thưởng và quyền đánh giá được cập nhật theo nghiệp vụ hiện có.

### Quy tắc an toàn

- Chỉ STAFF/ADMIN được xác nhận `shipped -> delivered`.
- Chỉ CUSTOMER sở hữu đơn được xác nhận `delivered -> completed`.
- `expected_updated_at` ngăn hai người xử lý đồng thời trên dữ liệu cũ.
- Mọi thay đổi đều đi qua state machine và được ghi lịch sử.

**Ảnh cần chèn:** thao tác “Xác nhận đã giao”, nút “Đã nhận hàng” và trạng thái đơn thay đổi realtime.

## 4.12. Một số đoạn mã nên minh họa

Chỉ chọn đoạn ngắn, có giải thích:

- Permission/ownership check.
- Transaction và row lock khi tạo order hoặc điều chỉnh tồn.
- Idempotency key/fingerprint.
- Hàm chuyển trạng thái `shipped -> delivered` có kiểm tra quyền và dữ liệu stale.
- State transition đơn hàng.
- Weighted average cost.
- WebSocket consumer hoặc notification service.
- Recommendation fallback.

## 4.13. Kết luận chương

Tóm tắt các module đã hiện thực và dẫn sang kết quả kiểm thử.

---

# CHƯƠNG 5. KIỂM THỬ VÀ ĐÁNH GIÁ

## 5.1. Chiến lược kiểm thử

- Unit test cho service, serializer, helper và component.
- API/integration test cho permission, ownership, transaction và state machine.
- PostgreSQL-specific test cho row lock/concurrency khi môi trường sẵn sàng.
- Frontend component test bằng Vitest.
- E2E bằng Playwright cho các luồng quan trọng.
- Static quality gate và OpenAPI validation.

## 5.2. Môi trường kiểm thử

Lập bảng:

| Thành phần | Môi trường kiểm thử |
|---|---|
| Hệ điều hành | Windows `[phiên bản thực tế]` |
| Backend | Python/Django local |
| Frontend | Node.js/pnpm/Vite local |
| Database | PostgreSQL Docker/local; SQLite chỉ dùng fallback một số lần |
| Redis | Docker/local |
| Trình duyệt | Chrome `[phiên bản]` |
| Payment | VNPay sandbox |

## 5.3. Test case chức năng tiêu biểu

### 5.3.1. Tài khoản và quyền

| Mã | Kịch bản | Kết quả mong đợi |
|---|---|---|
| TC-AUTH-01 | Đăng ký với email mới | Tạo CUSTOMER, password được hash |
| TC-AUTH-02 | Payload cố gán ADMIN | Bị bỏ qua/từ chối, không nâng quyền |
| TC-AUTH-03 | CUSTOMER gọi API admin | Trả 403 |
| TC-AUTH-04 | User A đọc địa chỉ User B | Trả 404/403 theo contract |
| TC-AUTH-05 | Access hết hạn, refresh hợp lệ | Tự lấy access mới một lần |

### 5.3.2. Catalog và kho

| Mã | Kịch bản | Kết quả mong đợi |
|---|---|---|
| TC-INV-01 | Điều chỉnh làm tồn âm | Từ chối |
| TC-INV-02 | Nhập hàng có giá nhập | Tăng tồn, cập nhật giá vốn bình quân |
| TC-INV-03 | Import CSV đúng mẫu | Tạo phiếu và các dòng nhập |
| TC-INV-04 | SKU trùng | Validation lỗi |
| TC-INV-05 | Sản phẩm ẩn | Không xuất hiện public API |

### 5.3.3. Đặt hàng và thanh toán

| Mã | Kịch bản | Kết quả mong đợi |
|---|---|---|
| TC-ORD-01 | Tạo COD hợp lệ | Tạo một order, trừ tồn, xóa cart item |
| TC-ORD-02 | Retry cùng idempotency key/payload | Trả order cũ, không tạo trùng |
| TC-ORD-03 | Cùng key, payload khác | Trả 409 |
| TC-ORD-04 | Hai checkout tranh tồn | Không oversell |
| TC-PAY-01 | VNPay signature sai | Không ghi paid |
| TC-PAY-02 | IPN thành công gửi lặp | Capture đúng một lần |

### 5.3.4. Voucher và đánh giá

| Mã | Kịch bản | Kết quả mong đợi |
|---|---|---|
| TC-VOU-01 | Voucher hết hạn | Không áp dụng |
| TC-VOU-02 | Concurrent usage chạm giới hạn | Không vượt usage limit |
| TC-REV-01 | Chưa mua nhưng đánh giá | Từ chối |
| TC-REV-02 | Review chưa duyệt | Không xuất hiện public |

### 5.3.5. Đổi hàng

| Mã | Kịch bản | Kết quả mong đợi |
|---|---|---|
| TC-EX-01 | Target variant khác product | Từ chối |
| TC-EX-02 | Quantity vượt số đã mua | Từ chối |
| TC-EX-03 | Inspection đạt | Cho chuẩn bị sản phẩm thay thế |
| TC-EX-04 | Reservation hết hạn | Hoàn tồn target đúng một lần |
| TC-EX-05 | Khách nhận hàng đổi | Request completed, order gốc không đổi |

### 5.3.6. Xác nhận giao và nhận hàng

| Mã | Kịch bản | Kết quả mong đợi |
|---|---|---|
| TC-DEL-01 | STAFF xác nhận đơn shipped đã giao | Chuyển delivered và ghi đúng actor/history |
| TC-DEL-02 | CUSTOMER gọi API chuyển delivered | Trả 403 |
| TC-DEL-03 | STAFF xác nhận từ trạng thái không hợp lệ | Trả 409 |
| TC-DEL-04 | Gửi `expected_updated_at` đã cũ | Trả 409 |
| TC-DEL-05 | Chủ đơn xác nhận đã nhận khi delivered | Chuyển completed |
| TC-DEL-06 | Khách khác xác nhận đơn không sở hữu | Trả 404/403 theo contract |

## 5.4. Kiểm thử bảo mật

- Horizontal authorization: truy cập ID của user khác.
- Vertical authorization: CUSTOMER gọi endpoint STAFF/ADMIN.
- CSRF với request cookie.
- CORS/Allowed Hosts.
- Refresh token cookie và logout.
- Upload sai loại/quá dung lượng.
- Brute-force throttle.
- Secret/log redaction.
- VNPay IPN sai chữ ký hoặc dữ liệu giao dịch bị thay đổi.

## 5.5. Kiểm thử đồng thời và tính nhất quán

- Hai người mua SKU cuối cùng.
- Hai request dùng cùng voucher giới hạn.
- Hai thao tác transition cùng expected timestamp.
- Callback thanh toán gửi lặp.
- Hai nhân viên duyệt cùng yêu cầu đổi.
- Phiếu nhập và checkout tác động cùng tồn kho.

## 5.6. Kết quả kiểm thử hiện có

Trình bày trung thực theo log dự án, không cộng dồn các mốc như cùng một lần chạy cuối:

- Các phase backend từng đạt từ 33 đến hơn 90 test tùy thời điểm/phạm vi.
- Phase 8 ghi nhận backend SQLite khoảng 95 test, một test PostgreSQL-only được bỏ qua.
- Frontend đạt 27 Vitest test ở mốc Phase 8, cùng typecheck, lint và production build.
- Fulfillment targeted suite kiểm tra luồng STAFF xác nhận đã giao và CUSTOMER xác nhận đã nhận.
- Ruff, Django check, migration drift và OpenAPI validation đã được chạy theo từng phase.
- Cần chạy lại full suite trên PostgreSQL/Redis/Docker ổn định trước khi chốt số liệu cuối báo cáo.

Trong bản Word chính thức, thay đoạn này bằng bảng kết quả từ lần chạy cuối cùng, gồm:

| Loại kiểm thử | Tổng | Pass | Fail | Skip | Ghi chú |
|---|---:|---:|---:|---:|---|
| Backend pytest | `[điền]` | `[điền]` | `[điền]` | `[điền]` | PostgreSQL/SQLite |
| Frontend Vitest | `[điền]` | `[điền]` | `[điền]` | `[điền]` | Component/unit |
| Playwright E2E | `[điền]` | `[điền]` | `[điền]` | `[điền]` | Desktop/mobile |
| OpenAPI validation | 1 | `[điền]` | `[điền]` | 0 | Schema contract |

## 5.7. Đánh giá kết quả đạt được

### Ưu điểm

- Bao phủ quy trình bán hàng từ catalog tới hậu mãi.
- Kiểm soát tồn kho, giá và tiền ở backend.
- Tách trạng thái order/payment/delivery/exchange rõ ràng.
- Permission và ownership không phụ thuộc frontend.
- Có idempotency, transaction, audit và chữ ký callback thanh toán.
- Giao diện tiếng Việt, responsive, light/dark và realtime.
- Có báo cáo giá vốn/lợi nhuận và recommendation có fallback.

### Hạn chế

- VNPay sandbox E2E với public HTTPS IPN chưa hoàn tất.
- Chưa triển khai production thật, object storage/CDN và monitoring đầy đủ.
- Recommendation mới ở popular/content/implicit baseline; chưa collaborative filtering.
- Chưa có dữ liệu người dùng thật để đánh giá conversion hoặc chất lượng recommendation.
- Một số lần test sử dụng SQLite/LocMem do Docker/PostgreSQL chưa ổn định.
- Chưa tích hợp theo dõi hành trình với đối tác vận chuyển thật; trạng thái giao hàng do nhân viên xác nhận.

## 5.8. Kết luận chương

Đánh giá mức độ đáp ứng mục tiêu và xác định công việc trước khi release.

---

# KẾT LUẬN VÀ HƯỚNG PHÁT TRIỂN

## 1. Kết luận

Tóm tắt:

- Đã xây dựng website bán giày và phụ kiện theo kiến trúc frontend/backend tách biệt.
- Đã hoàn thành các module tài khoản, catalog, kho, giỏ hàng, đơn hàng, thanh toán, tương tác, đổi hàng,
  recommendation, báo cáo, realtime và xác nhận giao/nhận hàng.
- Hệ thống chú trọng transaction, permission, ownership, idempotency và khả năng kiểm thử.
- Kết quả đáp ứng phần lớn mục tiêu đề tài trong môi trường development/sandbox.

## 2. Hướng phát triển

- Hoàn thiện Phase 10: E2E, security, concurrency, accessibility và performance.
- Chạy VNPay sandbox E2E qua public HTTPS IPN.
- Triển khai staging/production, HTTPS, reverse proxy và secure cookie.
- Dùng S3-compatible object storage/CDN cho ảnh.
- Thiết lập Celery/scheduler cho job định kỳ nếu tải tăng.
- Bổ sung monitoring, alert, centralized logging, backup/restore và secret rotation.
- Tích hợp hãng vận chuyển thật, tạo vận đơn và theo dõi hành trình.
- Bổ sung collaborative/hybrid recommendation khi đủ dữ liệu và đánh giá Recall@K/NDCG@K.
- Mở rộng chi phí vận chuyển/phí thanh toán vào báo cáo lợi nhuận.
- Nghiên cứu PWA, thông báo push và tìm kiếm nâng cao.

---

# TÀI LIỆU THAM KHẢO ĐỀ XUẤT

Chỉ đưa tài liệu thực sự đã đọc và ghi ngày truy cập nếu trường yêu cầu:

1. Django Documentation, phiên bản 5.2.
2. Django REST Framework Documentation.
3. Vue.js 3 Documentation.
4. TypeScript Documentation.
5. PostgreSQL Documentation.
6. Redis Documentation.
7. Django Channels Documentation.
8. OWASP Application Security Verification Standard/OWASP Cheat Sheets.
9. VNPay Sandbox Integration Documentation.
10. Fielding, R. T., “Architectural Styles and the Design of Network-based Software Architectures”.
11. Tài liệu về content-based recommendation, implicit feedback và ranking metrics.

Không trích dẫn blog không rõ tác giả nếu đã có tài liệu chính thức tương đương.

---

# PHỤ LỤC

## Phụ lục A. Hướng dẫn cài đặt và chạy hệ thống

- Yêu cầu Python, uv, Node, pnpm và Docker.
- Cấu hình PostgreSQL, Redis và `.env`.
- Migration và seed tài khoản/catalog/engagement.
- Chạy backend và frontend.
- Địa chỉ Swagger và frontend.

## Phụ lục B. Danh sách biến môi trường

Chỉ ghi tên và mục đích, không ghi secret thật:

- `DATABASE_URL`, `REDIS_URL`.
- `DJANGO_SECRET_KEY`, `JWT_SIGNING_KEY`.
- `EMAIL_*`, `FRONTEND_BASE_URL`.
- `VNPAY_TMN_CODE`, `VNPAY_HASH_SECRET`, `VNPAY_RETURN_URL`.
- Cookie/CORS/CSRF/Allowed Hosts settings.

## Phụ lục C. Danh sách API

Xuất từ OpenAPI schema/Swagger, nhóm theo module. Không cần dán toàn bộ schema YAML vào nội dung chính.

## Phụ lục D. Test case đầy đủ

- Mã test, tiền điều kiện, dữ liệu, bước thực hiện, kết quả mong đợi, kết quả thực tế và trạng thái.
- Đính kèm ảnh/log của các case quan trọng.

## Phụ lục E. Hình ảnh giao diện

- Storefront desktop/mobile.
- Auth/profile/address.
- Catalog/product/cart/checkout/order.
- Wishlist/review/exchange.
- Admin dashboard/catalog/inventory/order/engagement/report/staff/audit.
- Notification realtime và luồng xác nhận giao/nhận hàng.

## Phụ lục F. Kế hoạch phát triển theo phase

| Phase | Nội dung | Trạng thái hiện tại |
|---:|---|---|
| 0 | Khảo sát và chuẩn hóa base | Done |
| 1 | Tài khoản, RBAC và khung UI | Done |
| 2 | Catalog, SKU và kho | Done |
| 3 | Giỏ hàng và COD | Done |
| 4 | Fulfillment và VNPay | Done về code; sandbox E2E hoãn |
| 5 | Voucher, wishlist, review và banner | Chờ nghiệm thu |
| 6 | Đổi hàng không hoàn tiền | Chờ nghiệm thu |
| 7 | Recommendation và phụ kiện | Chờ nghiệm thu |
| 8 | Báo cáo, audit, realtime và vận hành | Chờ nghiệm thu |
| 9 | Xác nhận giao và nhận hàng | Đang triển khai/nghiệm thu |
| 10 | Kiểm thử tổng thể và release readiness | Chưa thực hiện |

---

# DANH MỤC HÌNH CẦN CHUẨN BỊ

1. Kiến trúc tổng thể hệ thống.
2. Use case tổng quát.
3. State machine đơn hàng.
4. State machine đổi hàng.
5. ERD tài khoản và catalog.
6. ERD đơn hàng và thanh toán.
7. ERD tương tác, đổi hàng và recommendation.
8. Sequence diagram đặt hàng COD.
9. Sequence diagram thanh toán VNPay.
10. Sequence diagram xác nhận giao và nhận hàng.
11. Sequence diagram đổi hàng.
12. Ảnh trang chủ và catalog.
13. Ảnh chi tiết sản phẩm và recommendation.
14. Ảnh giỏ hàng và checkout.
15. Ảnh danh sách/chi tiết đơn.
16. Ảnh dashboard admin.
17. Ảnh quản lý kho và nhập hàng.
18. Ảnh voucher/review/banner.
19. Ảnh xử lý đổi hàng.
20. Ảnh báo cáo và audit log.
21. Ảnh notification realtime.
22. Ảnh thao tác xác nhận đã giao và nút đã nhận hàng.

# DANH MỤC BẢNG CẦN CHUẨN BỊ

1. Bảng thuật ngữ và từ viết tắt.
2. Bảng so sánh quy trình cũ và hệ thống mới.
3. Bảng actor và quyền.
4. Bảng yêu cầu chức năng.
5. Bảng yêu cầu phi chức năng.
6. Bảng công nghệ sử dụng.
7. Bảng mô tả các bảng dữ liệu chính.
8. Bảng endpoint API tiêu biểu.
9. Bảng trạng thái đơn hàng.
10. Bảng trạng thái đổi hàng.
11. Bảng test case.
12. Bảng kết quả kiểm thử cuối cùng.
13. Bảng đánh giá ưu điểm/hạn chế.

---

# PROMPT ĐỂ ĐƯA CHO CHATGPT DỰNG THÀNH WORD

Sao chép nội dung từ đoạn dưới đây cùng toàn bộ đề cương phía trên:

```text
Bạn là chuyên gia viết báo cáo đồ án công nghệ thông tin bằng tiếng Việt. Hãy sử dụng đề cương và dữ liệu
dự án tôi cung cấp để biên soạn một báo cáo Word hoàn chỉnh cho đề tài “Xây dựng website bán giày và phụ
kiện Hải Duy Shop”.

Yêu cầu bắt buộc:
1. Giữ đúng cấu trúc phần đầu, Mở đầu, 5 chương, Kết luận, Tài liệu tham khảo và Phụ lục.
2. Viết theo văn phong học thuật, mạch lạc, có đoạn chuyển ý và nhận xét sau mỗi hình/bảng.
3. Không bịa số liệu, kết quả kiểm thử, người dùng, doanh thu hoặc trạng thái production. Chỗ thiếu dữ liệu
   phải giữ placeholder [CẦN BỔ SUNG].
4. Phân biệt rõ chức năng đã code, chức năng chờ nghiệm thu và hướng phát triển.
5. Không đưa secret, mật khẩu, mã merchant, khóa VNPay hoặc dữ liệu nhạy cảm vào báo cáo.
6. Dùng Heading chuẩn để Word tạo mục lục tự động; thêm caption Hình/Bảng và tham chiếu chéo.
7. Tạo các bảng yêu cầu, use case, mô tả dữ liệu, API, test case và kết quả kiểm thử theo đề cương.
8. Với sơ đồ chưa có ảnh, tạo khung mô tả [CHÈN HÌNH ...] kèm nội dung chính xác cần vẽ; không giả vờ đã
   có hình.
9. Đoạn mã chỉ dùng để minh họa, tối đa khoảng 20–30 dòng mỗi đoạn và phải giải thích.
10. Trích dẫn tài liệu chính thức, không tự tạo tài liệu tham khảo không tồn tại.

Trước khi xuất bản cuối, hãy liệt kê riêng những thông tin còn thiếu mà tôi cần cung cấp: thông tin sinh
viên/trường, yêu cầu định dạng của trường, ảnh giao diện, sơ đồ, số liệu test cuối cùng và tài liệu tham
khảo thực tế. Sau đó mới dựng nội dung Word.
```

