# Quyết định kiến trúc và chênh lệch hiện tại

## Cách ghi quyết định

Mỗi mục nêu lựa chọn, lý do, phạm vi, trạng thái (`hiện hành`/`dự kiến`) và lộ trình nếu source còn khác.
Không cần tạo quyết định cho chi tiết nhỏ; không sửa chuẩn chỉ để hợp thức hóa code mới.

## ADR-001 — Monorepo hai ứng dụng

- **Lựa chọn:** backend ở `Base_dijango/`, frontend ở `frontend/`; CI/tài liệu chung ở root.
- **Lý do:** phản ánh source hiện tại, không di chuyển hàng loạt hoặc làm hỏng import.
- **Phạm vi:** toàn repository.
- **Trạng thái:** hiện hành. Tên `dijango` sai chính tả được giữ vì đổi tên không đem lại giá trị trong
  nhiệm vụ chuẩn hóa; có thể đổi riêng sau khi cập nhật script/docs.

## ADR-002 — Backend modular monolith theo Django

- **Lựa chọn:** app theo nghiệp vụ; view/serializer/service/selector/model có trách nhiệm như chuẩn backend.
- **Lý do:** phù hợp code accounts hiện có và tránh controller/repository thừa.
- **Phạm vi:** backend.
- **Trạng thái:** hiện hành. Một vài truy vấn đơn giản còn ở serializer/service là chấp nhận được; chỉ
  chuyển sang selector khi phức tạp hoặc tái sử dụng.

## ADR-003 — Vue Composition API và module theo nghiệp vụ

- **Lựa chọn:** `<script setup lang="ts">`, TypeScript strict, Pinia chỉ cho shared state; API qua client chung.
- **Lý do:** đã nhất quán trong source và được toolchain enforce phần lớn.
- **Phạm vi:** frontend.
- **Trạng thái:** hiện hành. Các module hiện export qua `index.ts`; naming file đích chỉ áp dụng khi tách,
  không đổi hàng loạt.

## ADR-004 — Authentication cookie refresh/access memory

- **Lựa chọn:** refresh token HttpOnly cookie, access token memory, CSRF cho cookie-auth, refresh
  single-flight và retry 401 tối đa một lần; 403 không refresh.
- **Lý do:** giảm khả năng lộ refresh token qua JavaScript và tránh vòng interceptor.
- **Phạm vi:** frontend/backend auth.
- **Trạng thái:** hiện hành. Multi-tab dùng Web Locks/BroadcastChannel; fallback chỉ bảo đảm single-flight
  trong từng tab. Logout offline lưu cờ không nhạy cảm `logout-pending`, không lưu token.

## ADR-005 — API giữ snake_case và response DRF trực tiếp

- **Lựa chọn:** `/api/v1/`, trailing slash, JSON snake_case; frontend không mapping; response thành công
  không có envelope, lỗi có `code/message/details/request_id`.
- **Lý do:** khớp source/OpenAPI hiện tại, tránh lớp chuyển đổi không cần thiết.
- **Phạm vi:** API và frontend types.
- **Trạng thái:** hiện hành. Auth API đã dùng chung `ApiError` trong OpenAPI cho các error status được khai
  báo. Khi thêm endpoint hoặc error status, phải tiếp tục tham chiếu component này; runtime response không
  thay đổi.

## ADR-006 — Một formatter và một lockfile mỗi stack

- **Lựa chọn:** Ruff format cho Python; Prettier cho frontend; pnpm 11.19.0 với `pnpm-lock.yaml`.
- **Lý do:** tránh formatter/lockfile cạnh tranh và đồng nhất local/CI.
- **Phạm vi:** repository.
- **Trạng thái:** hiện hành sau chuẩn hóa. `package-lock.json` sinh nhầm không được commit.

## ADR-007 — Design system kế thừa token hiện có

- **Lựa chọn:** Soft UI Evolution sáng, Inter/system font, palette xanh và token trong `tokens.css`; base
  controls là điểm chứa native form controls.
- **Lý do:** UI hiện tại đã triển khai và có accessibility tốt. Kết quả UI UX Pro Max chung gợi ý cyberpunk
  không phù hợp nên không thay design system đã chốt.
- **Phạm vi:** frontend UI.
- **Trạng thái:** hiện hành. Quy tắc base control hiện được kiểm tra bằng tìm kiếm/review, chưa có custom
  lint để tránh tăng độ phức tạp.

## ADR-008 — Business role bằng Django Groups

- **Lựa chọn:** dùng Groups `CUSTOMER`, `STAFF`, `ADMIN` làm role bundle; permission/ownership được kiểm tra
  tại backend, frontend chỉ dùng role để điều hướng và trình bày.
- **Lý do:** tận dụng permission framework và Django Admin, tránh thêm role column làm nguồn sự thật thứ hai.
- **Phạm vi:** accounts và các API quản trị về sau.
- **Trạng thái:** hiện hành. Một user có thể thuộc nhiều group; đăng ký công khai luôn chỉ gán `CUSTOMER`.

## ADR-009 — Address invariant và password reset

- **Lựa chọn:** địa chỉ thuộc user, tối đa một default/user bằng conditional unique constraint; reset mật
  khẩu dùng Django token generator và phản hồi trung tính.
- **Lý do:** invariant quan trọng cần DB bảo vệ; token gắn với password state tự vô hiệu sau khi dùng.
- **Phạm vi:** accounts Phase 1.
- **Trạng thái:** hiện hành. Email local dùng console/LocMem; production cần provider được cấu hình.

## ADR-010 — Variant là đơn vị giá và tồn kho

- **Lựa chọn:** product giữ nội dung/publish; variant giữ SKU, size, color, Decimal price VND và balance.
  Size thuộc brand; stock movement là append-only và balance chỉ đổi qua transactional service.
- **Lý do:** đơn vị bán thực tế là SKU, đồng thời brand-size và lịch sử tồn là invariant nghiệp vụ.
- **Phạm vi:** catalog, cart/order và reporting về sau.
- **Trạng thái:** hiện hành. Row locking PostgreSQL cần integration test khi Docker DB sẵn sàng.

## ADR-011 — Event collection tối thiểu từ catalog

- **Lựa chọn:** client gửi view/recommendation impression/click qua allowlist schema v1 và idempotency UUID;
  không chấp nhận purchase do client khai báo.
- **Lý do:** thu dữ liệu sớm cho recommendation nhưng giảm PII, payload tự do và event giả có tác động cao.
- **Phạm vi:** catalog/recommendation analytics.
- **Trạng thái:** hiện hành; raw retention vẫn theo quyết định privacy ở phase sau.

## ADR-012 — Cart giá động, order snapshot và COD nguyên tử

- **Lựa chọn:** cart tham chiếu variant và luôn đọc giá hiện hành; quote/order được backend tính lại. Order
  lưu snapshot địa chỉ, sản phẩm và tiền. Tạo COD dùng idempotency UUID, transaction và row lock balance;
  trừ tồn lúc tạo order, hủy ở `pending_confirmation` hoàn tồn đúng một lần.
- **Lý do:** tránh tin dữ liệu giá từ client, giữ lịch sử đơn ổn định khi catalog thay đổi và ngăn double
  submit/oversell dưới cạnh tranh.
- **Phạm vi:** cart, checkout và COD order Phase 3.
- **Trạng thái:** hiện hành; PostgreSQL concurrency test đã xác minh hai checkout không thể bán vượt tồn.

## ADR-013 — VNPay IPN là nguồn xác nhận và tồn online dùng reservation

- **Lựa chọn:** order VNPay giữ available inventory 15 phút; payment attempt có reference/idempotency riêng.
  URL ký HMAC-SHA512 theo contract 2.1.0. Chỉ signed IPN đúng merchant/amount được cập nhật paid và capture
  reservation; Return URL frontend chỉ kích hoạt việc đọc lại trạng thái backend.
- **Lý do:** redirect có thể bị giả mạo/đóng giữa chừng, webhook có thể trùng hoặc sai thứ tự; reservation
  có expiry tránh giữ hàng vô hạn và tách rõ COD sale khỏi online payment pending.
- **Phạm vi:** order fulfillment, payment và inventory Phase 4.
- **Trạng thái:** hiện hành. IPN production cần HTTPS public URL đăng ký với VNPay. Signed browser return
  được backend xác minh bằng cùng checksum/merchant/amount/reference và xử lý idempotent như một fallback
  cho local/UX, nhưng không thay IPN vì khách có thể đóng trình duyệt trước khi quay lại merchant.

## ADR-014 — Voucher reservation và review verified-purchase

- **Lựa chọn:** voucher được kiểm tra lại dưới row lock khi tạo order; usage VNPay có vòng đời
  reserved/redeemed/released và discount dùng largest remainder theo line. Review gắn duy nhất với order
  item đã hoàn tất, customer edit đưa về pending và public chỉ thấy approved.
- **Lý do:** ngăn vượt giới hạn voucher dưới cạnh tranh, giữ tổng discount khớp tuyệt đối và không cho
  đánh giá giả hoặc nội dung chưa moderation xuất hiện công khai.
- **Phạm vi:** engagement, checkout/order và storefront Phase 5.
- **Trạng thái:** hiện hành; upload banner qua object storage được để cho phase tương ứng. Refund không
  nằm trong roadmap hiện tại.

## ADR-015 — Recommendation trong modular monolith và hoãn collaborative

- **Lựa chọn:** xếp hạng popular/content/personalized trực tiếp trong Django, lưu request/rank để attribution
  và dùng fallback deterministic. Catalog dùng loại sản phẩm cùng variant linh hoạt thay vì tạo module phụ
  kiện riêng.
- **Lý do:** quy mô hiện tại chưa cần ML service; sample data không đủ user/item density để collaborative
  filtering và offline evaluation có ý nghĩa. Một catalog giữ chung giá, kho, cart và order invariant.
- **Phạm vi:** catalog, storefront, cart/order attribution và dashboard recommendation Phase 7.
- **Trạng thái:** hiện hành. Chỉ triển khai collaborative/hybrid khi dữ liệu production vượt gate và kết
  quả Recall@K/NDCG@K/coverage tốt hơn baseline với latency chấp nhận được.

## Nợ kỹ thuật có kiểm soát

- Root ban đầu chưa là Git repository; người duy trì cần chạy quy trình init/push trong README.
- E2E không nằm trong CI mặc định vì cần full stack; chạy cho thay đổi auth/tích hợp và cân nhắc job riêng.
- Không có i18n; UI hiện quản lý nội dung tiếng Việt trực tiếp. Không cài i18n ngoài nhiệm vụ; nếu sản phẩm
  cần đa ngôn ngữ, chọn một hệ thống chung bằng ADR trước khi triển khai.
- ESLint chưa có rule sẵn để cấm native control ngoài `src/components/base`; dùng `rg` và review. Không viết
  custom linter phức tạp trong giai đoạn này.
- Auth đã đạt kiến trúc mục tiêu, nhưng token-family reuse detection/logout mọi thiết bị chưa có; đây là
  tính năng bảo mật riêng, không tự thay hợp đồng trong nhiệm vụ chuẩn hóa.

