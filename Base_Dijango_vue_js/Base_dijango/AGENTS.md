# Quy định backend

Đọc `../AGENTS.md`, `../docs/standards/backend.md`, `../docs/standards/api-contract.md` và
`docs/architecture.md` trước khi sửa backend.

- Giữ modular monolith và Django naming; không thêm controller/repository song song.
- View xử lý HTTP/permission/điều phối; serializer kiểm tra biên; service ghi nghiệp vụ; selector đọc phức tạp.
- Service không nhận request/serializer; selector không ghi dữ liệu; truy vấn đơn giản không bắt buộc bọc.
- Model đổi phải có migration cùng commit; không sửa migration đã dùng ở môi trường chung.
- Không đổi cơ chế JWT cookie/CSRF hoặc response contract ngoài phạm vi được yêu cầu.
- Public service, selector và helper phải có type hints; Python theo PEP 8/Ruff.
- Trước khi hoàn thành, chạy các gate backend liên quan trong root README.

