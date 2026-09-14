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
- **Trạng thái:** hiện hành. Chênh lệch: OpenAPI chưa gắn error schema chung cho tất cả error status.
- **Lộ trình:** thêm serializer/schema component cho error theo từng endpoint khi API được sửa, không đổi
  runtime response trong nhiệm vụ tài liệu.

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

## Nợ kỹ thuật có kiểm soát

- Root ban đầu chưa là Git repository; người duy trì cần chạy quy trình init/push trong README.
- E2E không nằm trong CI mặc định vì cần full stack; chạy cho thay đổi auth/tích hợp và cân nhắc job riêng.
- Không có i18n; UI hiện quản lý nội dung tiếng Việt trực tiếp. Không cài i18n ngoài nhiệm vụ; nếu sản phẩm
  cần đa ngôn ngữ, chọn một hệ thống chung bằng ADR trước khi triển khai.
- ESLint chưa có rule sẵn để cấm native control ngoài `src/components/base`; dùng `rg` và review. Không viết
  custom linter phức tạp trong giai đoạn này.
- Auth đã đạt kiến trúc mục tiêu, nhưng token-family reuse detection/logout mọi thiết bị chưa có; đây là
  tính năng bảo mật riêng, không tự thay hợp đồng trong nhiệm vụ chuẩn hóa.

