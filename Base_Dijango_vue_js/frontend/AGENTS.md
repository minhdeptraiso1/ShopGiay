# Quy định frontend

Đọc `../AGENTS.md`, `../docs/standards/frontend.md`, `../docs/standards/api-contract.md` và
`docs/design-system.md` trước khi sửa frontend.

- Code mới dùng Vue 3 Composition API, `<script setup lang="ts">` và TypeScript strict.
- Tôn trọng ranh giới pages/components/composables/stores/api/types/schemas đã chốt trong tài liệu chuẩn.
- Dùng `BaseButton`, `BaseLabel`, `BaseInput`, `FormField` và feedback/navigation component hiện có.
- Không gọi Axios hoặc hardcode endpoint trong page/shared UI; dùng client và API module chung.
- Không lưu access/refresh token trong Web Storage, không đổi auth/CSRF/API contract ngoài phạm vi.
- Dùng alias `@/` cho import xuyên vùng; import tương đối trong cùng module/component gần nhau.
- Trước khi hoàn thành, chạy các gate frontend liên quan trong root README.

