# Quy định làm việc trong repository

## Trước khi code (bắt buộc)

1. Đọc file `AGENTS.md` áp dụng cho file sắp sửa và tài liệu chuẩn liên quan.
2. Xác định module nghiệp vụ và tầng chịu trách nhiệm.
3. Dùng `rg` tìm chức năng tương tự, shared component, service, selector, helper, type, enum,
   serializer và validation có thể tái sử dụng.
4. Chọn một triển khai hiện có phù hợp làm mẫu; không tạo cách thứ hai chỉ do quen phong cách khác.
5. Xác định tác động đến API, database, migration hoặc shared component.
6. Với thay đổi đáng kể, nêu kế hoạch ngắn trước khi làm.
7. Chạy kiểm tra liên quan trước khi báo hoàn thành.

Nếu có nhiều cách hiện hữu, theo quyết định trong `docs/standards/architecture-decisions.md`. Nếu chưa có
quyết định, chọn theo source thực tế và ghi lại; chỉ hỏi khi lựa chọn làm đổi đáng kể phạm vi, dữ liệu hoặc
tính tương thích. Không refactor hàng loạt ngoài nhiệm vụ.

## Quy định chung (bắt buộc)

- Một thành phần có một trách nhiệm; nghiệp vụ ở module sở hữu, shared code không phụ thuộc module cụ thể.
- Kiểm tra khả năng tái sử dụng trước khi tạo mới; không tạo abstraction/utils chung chung thiếu ranh giới.
- Không thêm dependency khi công cụ hiện có đủ dùng.
- Không nuốt lỗi, trả thành công giả, hardcode secret/credential/URL môi trường hoặc log token, cookie,
  password, `Authorization`.
- Không để mock, code tạm hoặc TODO thay phần phải hoàn thành. Comment giải thích lý do/giới hạn.
- Giữ diff tập trung; không format file ngoài phạm vi. Đổi API/kiến trúc phải cập nhật tài liệu nguồn.

Hướng dẫn chi tiết có thể linh hoạt khi source cũ bắt buộc, nhưng ngoại lệ phải được giải thích trong báo
cáo. Không dùng giới hạn số dòng tùy tiện; tách theo trách nhiệm và độ phức tạp.

## Phạm vi và nguồn chính thức

- Frontend: `frontend/AGENTS.md`, `docs/standards/frontend.md`, `frontend/docs/design-system.md`.
- Backend: `Base_dijango/AGENTS.md`, `docs/standards/backend.md`, `Base_dijango/docs/architecture.md`.
- API/auth: `docs/standards/api-contract.md`.
- Quyết định và chênh lệch hiện tại: `docs/standards/architecture-decisions.md`.

## Điều kiện hoàn thành

- Backend: Ruff lint/format, Django check, migration check, pytest và OpenAPI validation theo README.
- Frontend: typecheck, ESLint, Prettier check, Vitest và build theo README; chạy E2E khi đổi luồng tích hợp.
- Không cần chạy toàn bộ E2E cho thay đổi chỉ có tài liệu.
- Báo cáo phải nêu thay đổi/lý do, phần đã tái sử dụng, lệnh đã chạy, giới hạn chưa xác minh và ngoại lệ.

