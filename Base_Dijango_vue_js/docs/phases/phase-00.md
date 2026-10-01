# Phase 0 - Khảo sát và chuẩn hóa base

**Trạng thái:** Done
**Nhánh đề xuất:** `phase/00-base`  
**Phụ thuộc:** Không

## Mục tiêu

Xác nhận base Django REST + Vue có thể chạy lặp lại, ghi nhận hiện trạng và chỉ sửa lỗi nền đã được chứng
minh. Không triển khai chức năng commerce hoặc Phase 1.

## Hiện trạng 0A

- Đã đọc `AGENTS.md`, standards, manifests, auth, routing, settings, model, migration, test và CI.
- Working tree sạch; `.env` backend tồn tại nhưng được ignore.
- Chưa chạy quality gate vì chưa có `uv`, backend environment và `frontend/node_modules`.
- Node 24 và Python 3.12 phù hợp; pnpm hệ thống 12 khác pnpm 11.19.0 được khóa trong dự án.
- Không sửa source, cài dependency, chạy migration hoặc truy cập dữ liệu.

## Sprint 0B-S01 - Baseline có thể tái lập

| ID | Loại | Công việc | Phụ thuộc | Đầu ra / nghiệm thu | Trạng thái |
|---|---|---|---|---|---|
| P00-S01-DOC01 | Docs | Tạo audit, business rules và progress log không trùng tài liệu hiện có | Approval | Tài liệu phản ánh source thực tế | Completed |
| P00-S01-INT01 | Integration | Cài dependency đúng lockfile, không nâng version | Approval | `uv sync --frozen`, pnpm 11.19 frozen install thành công | Completed |
| P00-S01-TEST01 | Test | Chạy backend gates | INT01, test DB/Redis | Static gates pass; 23 pytest pass bằng SQLite/LocMem; PostgreSQL/Redis chưa xác minh do Docker daemon | Blocked |
| P00-S01-TEST02 | Test | Chạy frontend gates | INT01 | Typecheck, lint, format check, 10 Vitest test và build pass | Completed |
| P00-S01-TEST03 | Test | Chạy E2E auth nếu full stack sẵn sàng | TEST01-02 | Chưa chạy vì PostgreSQL/Redis/Docker chưa sẵn sàng | Blocked |

## Sprint 0B-S02 - Sửa và chuẩn hóa nền

| ID | Loại | Công việc | Phụ thuộc | Đầu ra / nghiệm thu | Trạng thái |
|---|---|---|---|---|---|
| P00-S02-BE01 | BE | Sửa lỗi backend do baseline phát hiện, không đổi contract ngoài duyệt | S01 | Cookie contract test chạy ổn định trên Windows | Completed |
| P00-S02-FE01 | FE | Sửa lỗi frontend do baseline phát hiện | S01 | Frontend gates pass với cache và line ending Windows | Completed |
| P00-S02-API01 | BE/Docs | Đồng bộ tài liệu logout với source idempotent hiện tại | S01 | Source, test và docs không mâu thuẫn | Completed |
| P00-S02-API02 | BE/Test | Gắn error schema chung cho API auth hiện có | S01 | OpenAPI validate không warning, runtime contract không đổi | Completed |
| P00-S02-DOC01 | Docs | Chuẩn hóa hướng dẫn tool/version/path local | S01 | README không còn phụ thuộc đường dẫn máy cá nhân | Completed |

## Ảnh hưởng dự kiến

- Màn hình/API: không thêm; giữ nguyên năm endpoint auth.
- Database: không dự kiến đổi model hay migration.
- File chính: docs, OpenAPI snapshot và lỗi nền nếu quality gate chứng minh.
- Dependency: chỉ cài từ lockfile; mọi đề xuất thêm/nâng dependency phải xin duyệt riêng.

## Tiêu chí nghiệm thu

- Hai stack cài được từ lockfile và các gate liên quan pass hoặc có blocker được chứng minh.
- Không có secret, `.env`, cache hay build artifact bị track.
- Không có chức năng Phase 1 trở đi và không có migration ngoài phạm vi.
- Báo cáo lệnh đã chạy, kết quả, phần chưa kiểm chứng và trạng thái `Awaiting acceptance`.

## Kết quả thực hiện

- Backend: Ruff lint/format, Django check, migration drift và OpenAPI validation pass.
- Backend fallback: 23/23 pytest pass, coverage 90% trên SQLite + LocMem.
- Frontend: typecheck, ESLint, Prettier, 10/10 Vitest tests và production build pass.
- Chưa xác minh: PostgreSQL/Redis pytest và browser E2E vì Docker daemon không phản hồi.
- Không có model change hoặc migration mới; không triển khai chức năng Phase 1.

## Approval gate

Phase 0 đã được người dùng nghiệm thu khi duyệt và yêu cầu bắt đầu Phase 1 ngày 2026-09-14.
