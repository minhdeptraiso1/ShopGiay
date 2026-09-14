# Phase 0 - Khảo sát và chuẩn hóa base

**Trạng thái:** Awaiting approval  
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
| P00-S01-DOC01 | Docs | Tạo audit, business rules và progress log không trùng tài liệu hiện có | Approval | Tài liệu phản ánh source thực tế | Awaiting approval |
| P00-S01-INT01 | Integration | Cài dependency đúng lockfile, không nâng version | Approval | `uv sync --frozen`, pnpm 11.19 frozen install thành công | Awaiting approval |
| P00-S01-TEST01 | Test | Chạy backend gates | INT01, test DB/Redis | Ruff, Django check, migration check, pytest, OpenAPI có kết quả | Awaiting approval |
| P00-S01-TEST02 | Test | Chạy frontend gates | INT01 | Typecheck, lint, format check, Vitest, build có kết quả | Awaiting approval |
| P00-S01-TEST03 | Test | Chạy E2E auth nếu full stack sẵn sàng | TEST01-02 | CSRF, cookie, reload, profile, logout pass | Awaiting approval |

## Sprint 0B-S02 - Sửa và chuẩn hóa nền

| ID | Loại | Công việc | Phụ thuộc | Đầu ra / nghiệm thu | Trạng thái |
|---|---|---|---|---|---|
| P00-S02-BE01 | BE | Sửa lỗi backend do baseline phát hiện, không đổi contract ngoài duyệt | S01 | Backend gates pass | Awaiting approval |
| P00-S02-FE01 | FE | Sửa lỗi frontend do baseline phát hiện | S01 | Frontend gates pass | Awaiting approval |
| P00-S02-API01 | BE/Docs | Đồng bộ tài liệu logout với source idempotent hiện tại | S01 | Source, test và docs không mâu thuẫn | Awaiting approval |
| P00-S02-API02 | BE/Test | Gắn error schema chung cho API auth hiện có | S01 | OpenAPI validate không warning, runtime contract không đổi | Awaiting approval |
| P00-S02-DOC01 | Docs | Chuẩn hóa hướng dẫn tool/version/path local | S01 | Máy mới làm theo một quy trình duy nhất | Awaiting approval |

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

## Approval gate

Lệnh xác nhận: **`Duyệt Phase 0`**. Việc tạo bộ tài liệu phase không tự động duyệt phần cài đặt hoặc sửa
source của Phase 0B.

